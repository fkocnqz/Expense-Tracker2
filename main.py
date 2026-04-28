import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("850x550")
        self.expenses = []
        self.load_data()
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # === ФОРМА ДОБАВЛЕНИЯ ===
        add_frame = ttk.LabelFrame(self.root, text="➕ Добавить расход", padding=10)
        add_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(add_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(add_frame, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar(value="Еда")
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var, width=15,
                                           values=["Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"])
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(add_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(add_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10, pady=5)

        # === ФИЛЬТРЫ И РАСЧЁТ ===
        filter_frame = ttk.LabelFrame(self.root, text="🔍 Фильтрация и расчёт за период", padding=10)
        filter_frame.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_cat_var = tk.StringVar(value="Все")
        self.filter_cat_combo = ttk.Combobox(filter_frame, textvariable=self.filter_cat_var, width=15,
                                             values=["Все", "Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"])
        self.filter_cat_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Период с:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.start_date_entry.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))

        ttk.Label(filter_frame, text="По:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=6, padx=10, pady=5)

        # === ТАБЛИЦА ===
        self.tree = ttk.Treeview(self.root, columns=("ID", "Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Сумма", width=100, anchor="e")
        self.tree.column("Категория", width=130, anchor="center")
        self.tree.column("Дата", width=110, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # === ИТОГО ===
        total_frame = ttk.Frame(self.root, padding=10)
        total_frame.pack(fill=tk.X, padx=15, pady=5)
        self.total_label = ttk.Label(total_frame, text="Итого за выбранный период: 0.00", font=("Segoe UI", 12, "bold"))
        self.total_label.pack(side=tk.RIGHT)

    def validate_input(self, amount_str, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть положительным числом."
        except ValueError:
            return False, "Сумма должна быть корректным числом."

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Дата должна быть в формате YYYY-MM-DD."

        return True, amount

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()

        is_valid, result = self.validate_input(amount_str, date_str)
        if not is_valid:
            messagebox.showerror("Ошибка ввода", result)
            return

        new_id = max((e["id"] for e in self.expenses), default=0) + 1
        self.expenses.append({
            "id": new_id,
            "amount": result,
            "category": category,
            "date": date_str
        })
        self.save_data()
        self.apply_filters()
        self.amount_entry.delete(0, tk.END)

    def update_table(self, data=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        displayed = data if data is not None else self.expenses
        for exp in displayed:
            self.tree.insert("", tk.END, values=(exp["id"], exp["amount"], exp["category"], exp["date"]))
        total = sum(exp["amount"] for exp in displayed)
        self.total_label.config(text=f"Итого за выбранный период: {total:.2f}")

    def apply_filters(self):
        cat = self.filter_cat_var.get()
        try:
            start = datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка фильтра", "Даты периода должны быть в формате YYYY-MM-DD.")
            return

        if start > end:
            start, end = end, start  # Автоисправление порядка дат

        filtered = []
        for exp in self.expenses:
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
            cat_ok = (cat == "Все" or exp["category"] == cat)
            date_ok = start <= exp_date <= end
            if cat_ok and date_ok:
                filtered.append(exp)

        self.update_table(filtered)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.expenses = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
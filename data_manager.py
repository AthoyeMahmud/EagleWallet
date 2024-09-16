import sqlite3
import pandas as pd
from expense_model import Expense

class DataManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            username TEXT,
            amount REAL,
            category TEXT,
            date TEXT,
            description TEXT
        )
        ''')
        self.conn.commit()

    def register_user(self, user):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                       (user.username, user.password, user.email))
        self.conn.commit()

    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        return user is not None

    def add_expense(self, expense):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO expenses (username, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                       (expense.username, expense.amount, expense.category, expense.date, expense.description))
        self.conn.commit()

    def get_user_expenses(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE username = ?", (username,))
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Username", "Amount", "Category", "Date", "Description"])
        return df

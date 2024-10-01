import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import pandas as pd
import plotly.express as px
from abc import ABC, abstractmethod

# Database setup
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, category TEXT, date TEXT, currency TEXT)''')

conn.commit()

class User:
    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    def save(self):
        hashed_password = pbkdf2_sha256.hash(self.password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (self.username, hashed_password))
        conn.commit()

    @staticmethod
    def authenticate(username, password):
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result:
            return pbkdf2_sha256.verify(password, result[0])
        return False

class Expense(ABC):
    def __init__(self, user_id, amount, category, date, currency):
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.date = date
        self.currency = currency

    @abstractmethod
    def save(self):
        pass

class ManualExpense(Expense):
    def save(self):
        c.execute("INSERT INTO expenses (user_id, amount, category, date, currency) VALUES (?, ?, ?, ?, ?)",
                  (self.user_id, self.amount, self.category, self.date, self.currency))
        conn.commit()

class ExpenseTracker:
    def __init__(self, user_id):
        self.user_id = user_id

    def add_expense(self, amount, category, date, currency):
        expense = ManualExpense(self.user_id, amount, category, date, currency)
        expense.save()

    def get_expenses(self):
        c.execute("SELECT * FROM expenses WHERE user_id = ?", (self.user_id,))
        return c.fetchall()

    def generate_report(self):
        expenses = self.get_expenses()
        df = pd.DataFrame(expenses, columns=['id', 'user_id', 'amount', 'category', 'date', 'currency'])
        return df

    def visualize_expenses(self):
        df = self.generate_report()
        fig = px.pie(df, values='amount', names='category', title='Expense Distribution')
        return fig

def main():
    st.title("Expense Tracker App")

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if st.session_state.user_id is None:
        auth_option = st.radio("Choose an option:", ("Login", "Register"))

        if auth_option == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if User.authenticate(username, password):
                    c.execute("SELECT id FROM users WHERE username = ?", (username,))
                    st.session_state.user_id = c.fetchone()[0]
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid username or password")

        else:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Register"):
                user = User(username, password)
                try:
                    user.save()
                    st.success("Registered successfully! Please log in.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")

    else:
        tracker = ExpenseTracker(st.session_state.user_id)

        st.header("Add Expense")
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Utilities", "Other"])
        date = st.date_input("Date")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY"])

        if st.button("Add Expense"):
            tracker.add_expense(amount, category, date.strftime("%Y-%m-%d"), currency)
            st.success("Expense added successfully!")

        st.header("Expense Report")
        report = tracker.generate_report()
        st.dataframe(report)

        st.header("Expense Visualization")
        fig = tracker.visualize_expenses()
        st.plotly_chart(fig)

        if st.button("Logout"):
            st.session_state.user_id = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
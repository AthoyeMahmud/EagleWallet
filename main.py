!pip install streamlit pandas matplotlib plotly scikit-learn openai

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime

# OOP for Expense Tracker
class Expense:
    def __init__(self, description, amount, date, category):
        self.description = description
        self.amount = amount
        self.date = date
        self.category = category

class ExpenseTracker:
    def __init__(self):
        self.expenses = pd.DataFrame(columns=["Description", "Amount", "Date", "Category"])

    def add_expense(self, expense):
        new_expense = {"Description": expense.description,
                       "Amount": expense.amount,
                       "Date": expense.date,
                       "Category": expense.category}
        self.expenses = self.expenses.append(new_expense, ignore_index=True)

    def delete_expense(self, index):
        self.expenses = self.expenses.drop(index)

    def get_expenses(self):
        return self.expenses

    def export_data(self, file_format):
        if file_format == "CSV":
            self.expenses.to_csv("expenses.csv", index=False)
            return "Expenses exported as CSV."
        elif file_format == "Excel":
            self.expenses.to_excel("expenses.xlsx", index=False)
            return "Expenses exported as Excel."

# Streamlit App
st.title("💸 Expense Tracker with GPT and Predictions")
st.sidebar.header("Add a New Expense")

# Initialize ExpenseTracker
tracker = ExpenseTracker()

# Input form for expenses
description = st.sidebar.text_input("Expense Description")
amount = st.sidebar.number_input("Expense Amount", min_value=0.0, format="%.2f")
category = st.sidebar.selectbox("Category", ["Food", "Transport", "Bills", "Shopping", "Others"])
date = st.sidebar.date_input("Date", datetime.date.today())

if st.sidebar.button("Add Expense"):
    if description and amount:
        expense = Expense(description, amount, date, category)
        tracker.add_expense(expense)
        st.sidebar.success("Expense added!")

# Display expenses
st.header("Current Expenses")
expenses_df = tracker.get_expenses()
if not expenses_df.empty:
    st.write(expenses_df)

# Visualization - Expense by Category
if not expenses_df.empty:
    st.header("Visualization")
    fig = px.pie(expenses_df, values="Amount", names="Category", title="Expenses by Category")
    st.plotly_chart(fig)

# Export data option
st.sidebar.header("Export Data")
export_format = st.sidebar.selectbox("Choose format", ["CSV", "Excel"])
if st.sidebar.button("Export"):
    export_message = tracker.export_data(export_format)
    st.sidebar.success(export_message)

# Prediction using Linear Regression
st.header("Predict Future Expenses")
if not expenses_df.empty:
    # Simple Linear Regression for predicting expenses
    expenses_df["Date"] = pd.to_datetime(expenses_df["Date"])
    expenses_df["Days"] = (expenses_df["Date"] - expenses_df["Date"].min()).dt.days
    X = expenses_df["Days"].values.reshape(-1, 1)
    y = expenses_df["Amount"].values

    if len(X) > 1:
        model = LinearRegression()
        model.fit(X, y)

        future_days = np.array([X[-1] + i for i in range(1, 31)]).reshape(-1, 1)
        future_predictions = model.predict(future_days)

        st.write("Predicted expenses for the next 30 days:")
        st.line_chart(future_predictions)
    else:
        st.warning("Not enough data for predictions.")

# Budget Alert System
st.sidebar.header("Budget Alert")
budget_limit = st.sidebar.number_input("Set a budget limit", min_value=0.0, format="%.2f")
if not expenses_df.empty and budget_limit:
    total_expense = expenses_df["Amount"].sum()
    if total_expense > budget_limit:
        st.sidebar.error(f"Alert! You have exceeded your budget by ${total_expense - budget_limit:.2f}.")

# GPT Integration (Streamlit native chatbot)
st.header("💬 Chat with GPT")
st.chat_input("Ask me anything about your expenses!")

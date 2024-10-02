import streamlit as st
import pandas as pd
import plotly.express as px
from forex_python.converter import CurrencyRates
import pytesseract
from PIL import Image
import numpy as np
from sklearn.linear_model import LinearRegression
import random
from datetime import datetime, timedelta

# Initialize session state for expenses and goals
def initialize_session_state():
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount', 'Currency'])
    if 'goals' not in st.session_state:
        st.session_state.goals = pd.DataFrame(columns=['Goal', 'Target Amount', 'Current Amount'])

initialize_session_state()

# Function to automatically categorize expenses based on description
def categorize_expense(description):
    keywords = {
        'food': ['restaurant', 'grocery', 'food'],
        'travel': ['flight', 'hotel', 'taxi', 'uber'],
        'shopping': ['clothing', 'electronics', 'mall'],
        'entertainment': ['movie', 'cinema', 'concert'],
        'health': ['doctor', 'medicine', 'pharmacy'],
        'other': ['other']
    }
    for category, words in keywords.items():
        if any(word in description.lower() for word in words):
            return category
    return 'other'

# Utility for converting currencies
def convert_currency(amount, from_currency, to_currency):
    c = CurrencyRates()
    try:
        return c.convert(from_currency, to_currency, amount)
    except Exception as e:
        st.error(f"Currency conversion failed: {e}")
        return None

# Sidebar navigation
st.sidebar.title("Enhanced Expense Tracker")
option = st.sidebar.radio('Menu', ['Home', 'Add Expense', 'Receipt Scanning', 'Expense Visualization',
                                   'Goal Tracking', 'Expense Prediction', 'Travel Budgeting', 'Debt Tracking',
                                   'Generate Sample Data', 'Import/Export'])

# Main content area
if option == 'Home':
    st.header("Welcome to the Enhanced Expense Tracker App!")
    st.write("""
    This app helps you manage and track your expenses, scan receipts, set goals, predict spending trends, and much more!
    Use the sidebar to navigate through different features.
    """)

elif option == 'Add Expense':
    st.header("Add a New Expense")
    date = st.date_input("Expense Date")
    description = st.text_input("Description")
    category = st.selectbox("Expense Category", ["Auto", "Bills", "Entertainment", "Food", "Shopping", "Travel", "Other"])
    amount = st.number_input("Amount")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR", "JPY"])

    if st.button("Add Expense"):
        new_expense = {"Date": date, "Category": category, "Description": description, "Amount": amount, "Currency": currency}
        st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_expense])], ignore_index=True)
        st.success(f"Added {category} expense of {amount} {currency}!")

elif option == 'Receipt Scanning':
    st.header("Receipt Scanning")
    uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Receipt", use_column_width=True)
        receipt_text = pytesseract.image_to_string(img)
        st.text_area("Extracted Text", receipt_text)
        category = categorize_expense(receipt_text)
        amount = st.number_input("Enter the amount (as scanned may be inaccurate)", min_value=0.0)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR", "JPY"])

        if st.button("Save Scanned Expense"):
            new_expense = {"Date": pd.Timestamp.today(), "Category": category, "Description": receipt_text, "Amount": amount, "Currency": currency}
            st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_expense])], ignore_index=True)
            st.success(f"Scanned {category} expense of {amount} {currency}!")

elif option == 'Expense Visualization':
    st.header("Expense Visualization")
    if st.session_state.expenses.empty:
        st.warning("No expenses recorded yet. Please add expenses first.")
    else:
        selected_currency = st.selectbox("View expenses in currency", ["USD", "EUR", "GBP", "INR", "JPY"])
        filtered_expenses = st.session_state.expenses.copy()

        # Apply conversion efficiently
        def convert_row(row):
            if row['Currency'] != selected_currency:
                return convert_currency(row['Amount'], row['Currency'], selected_currency)
            return row['Amount']

        filtered_expenses['Amount'] = filtered_expenses.apply(lambda row: convert_row(row), axis=1)
        filtered_expenses['Currency'] = selected_currency
        fig = px.bar(filtered_expenses, x="Date", y="Amount", color="Category", barmode="group", title=f"Expenses in {selected_currency}")
        st.plotly_chart(fig)

elif option == 'Goal Tracking':
    st.header("Track Your Goals")
    st.subheader("Your Goals")
    if st.session_state.goals.empty:
        st.write("No goals set yet.")
    else:
        st.write(st.session_state.goals)

    st.subheader("Set a New Goal")
    goal_name = st.text_input("Goal Name")
    target_amount = st.number_input("Target Amount")
    current_amount = st.number_input("Current Amount", min_value=0.0)

    if st.button("Add Goal"):
        new_goal = {"Goal": goal_name, "Target Amount": target_amount, "Current Amount": current_amount}
        st.session_state.goals = pd.concat([st.session_state.goals, pd.DataFrame([new_goal])], ignore_index=True)
        st.success(f"Added goal '{goal_name}' with a target of {target_amount}!")

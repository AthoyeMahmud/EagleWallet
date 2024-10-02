import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import secrets

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'password' not in st.session_state:
    st.session_state.password = ''
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# Function to hash password
def hash_password(password):
    salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    hashed_password = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return salt + hashed_password

# Function to verify password
def verify_password(stored_password, provided_password):
    salt = stored_password[:16]
    stored_password = stored_password[16:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    hashed_password = base64.urlsafe_b64encode(kdf.derive(provided_password.encode()))
    return hashed_password == stored_password

# Function to add expense
def add_expense(date, category, amount, description):
    expense = {
        'date': date,
        'category': category,
        'amount': amount,
        'description': description
    }
    st.session_state.expenses.append(expense)

# Function to delete expense
def delete_expense(index):
    del st.session_state.expenses[index]

# Function to update expense
def update_expense(index, date, category, amount, description):
    st.session_state.expenses[index] = {
        'date': date,
        'category': category,
        'amount': amount,
        'description': description
    }

# Function to calculate total expenses
def calculate_total_expenses():
    total = 0
    for expense in st.session_state.expenses:
        total += expense['amount']
    return total

# Function to calculate expenses by category
def calculate_expenses_by_category():
    categories = {}
    for expense in st.session_state.expenses:
        if expense['category'] in categories:
            categories[expense['category']] += expense['amount']
        else:
            categories[expense['category']] = expense['amount']
    return categories

# Main application
st.title("Expense Tracker")

# Login form
if not st.session_state.logged_in:
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            try:
                with open("users.txt", "r") as file:
                    users = file.readlines()
                    for user in users:
                        user = user.strip().split(",")
                        if user[0] == username and verify_password(user[1].encode(), password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.password = password
                            break
                    else:
                        st.error("Invalid username or password")
            except FileNotFoundError:
                st.error("No users found")

# Register form
if not st.session_state.logged_in:
    with st.form("register"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            try:
                with open("users.txt", "a") as file:
                    hashed_password = hash_password(password)
                    file.write(f"{username},{hashed_password.decode()}\n")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.password = password
            except Exception as e:
                st.error(str(e))

# Add expense form
if st.session_state.logged_in:
    st.subheader("Add Expense")
    with st.form("add_expense"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Other"])
        amount = st.number_input("Amount")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            add_expense(date, category, amount, description)

# View expenses
if st.session_state.logged_in:
    st.subheader("View Expenses")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        st.write(df)
    else:
        st.write("No expenses added yet.")

# Delete expense
if st.session_state.logged_in:
    st.subheader("Delete Expense")
    if st.session_state.expenses:
        index = st.selectbox("Select Expense to Delete", range(len(st.session_state.expenses)))
        if st.button("Delete Expense"):
            delete_expense(index)
    else:
        st.write("No expenses added yet.")

# Update expense
if st.session_state.logged_in:
    st.subheader("Update Expense")
    if st.session_state.expenses:
        index = st.selectbox("Select Expense to Update", range(len(st.session_state.expenses)))
        with st.form("update_expense"):
            date = st.date_input("Date", value=st.session_state.expenses[index]['date'])
            category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Other"], index=["Food", "Transportation", "Entertainment", "Other"].index(st.session_state.expenses[index]['category']))
            amount = st.number_input("Amount", value=st.session_state.expenses[index]['amount'])
            description = st.text_input("Description", value=st.session_state.expenses[index]['description'])
            submitted = st.form_submit_button("Update Expense")

            if submitted:
                update_expense(index, date, category, amount, description)
    else:
        st.write("No expenses added yet.")

# Calculate total expenses
if st.session_state.logged_in:
    st.subheader("Total Expenses")
    total_expenses = calculate_total_expenses()
    st.write(f"Total Expenses: ${total_expenses:.2f}")

# Calculate expenses by category
if st.session_state.logged_in:
    st.subheader("Expenses by Category")
    expenses_by_category = calculate_expenses_by_category()
    st.write(expenses_by_category)

# Plot expenses by category
if st.session_state.logged_in:
    st.subheader("Expenses by Category Plot")
    fig = px.bar(x=list(expenses_by_category.keys()), y=list(expenses_by_category.values()))
    fig.update_layout(title="Expenses by Category", xaxis_title="Category", yaxis_title="Amount")
    st.plotly_chart(fig)
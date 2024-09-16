import streamlit as st
import pandas as pd
from data_manager import DataManager
from gpt_financial_assistant import ask_financial_advisor
from expense_model import User, Expense, Income, Budget

# Initialize data manager
data_manager = DataManager('budget.db')

# Streamlit app setup
st.title("Budget Tracker with AI Assistant")

# User Login and Registration
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Sign Up":
    st.subheader("Create New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    email = st.text_input("Email")
    
    if st.button("Sign Up"):
        user = User(username, password, email)
        data_manager.register_user(user)
        st.success("Account created successfully! Go to the login menu.")

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if data_manager.login_user(username, password):
            st.success(f"Welcome, {username}!")
            
            # Dashboard and Features
            st.header("Expense Tracker")
            expense_data = data_manager.get_user_expenses(username)
            
            if not expense_data.empty:
                st.write("Your Expenses:")
                st.dataframe(expense_data)
            else:
                st.write("No expenses recorded yet.")
            
            # Add New Expense
            st.subheader("Add New Expense")
            amount = st.number_input("Amount", min_value=0.0)
            category = st.selectbox("Category", ["Food", "Transport", "Rent", "Others"])
            date = st.date_input("Date")
            description = st.text_area("Description")
            
            if st.button("Add Expense"):
                expense = Expense(username, amount, category, date, description)
                data_manager.add_expense(expense)
                st.success(f"Expense of {amount} added.")
            
            # AI Financial Assistant - GPT Integration
            st.header("Ask Your Financial Assistant")
            user_query = st.text_input("Ask something about your expenses:")
            if st.button("Ask GPT"):
                response = ask_financial_advisor(user_query)
                st.write(response)
        else:
            st.error("Incorrect login details")


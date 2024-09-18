import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_manager import DataManager
from expense_model import User, Expense, Budget
import datetime

# Initialize data manager
data_manager = DataManager('budget.db')

# Streamlit app setup
st.title("Budget Tracker with GPT-powered Assistant")

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

            # Visualizing Expenses
            if not expense_data.empty:
                st.write("Your Expenses:")
                st.dataframe(expense_data)
                
                # Visualization - Pie chart for categories
                st.subheader("Expense Breakdown by Category")
                category_sum = expense_data.groupby("Category").sum()["Amount"]
                fig, ax = plt.subplots()
                ax.pie(category_sum, labels=category_sum.index, autopct='%1.1f%%')
                st.pyplot(fig)
                
                # Visualization - Line chart for daily expenses
                st.subheader("Expense Trend Over Time")
                expense_data["Date"] = pd.to_datetime(expense_data["Date"])
                daily_expenses = expense_data.groupby("Date").sum()["Amount"]
                st.line_chart(daily_expenses)

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
                
            # Set and Monitor Budget Limit
            st.subheader("Set Your Monthly Budget")
            total_budget = st.number_input("Total Monthly Budget", min_value=0.0)
            if st.button("Set Budget"):
                budget = Budget(username, total_budget)
                data_manager.set_budget(budget)
                st.success(f"Monthly budget set at {total_budget}.")
            
            current_month = datetime.date.today().strftime("%Y-%m")
            monthly_expenses = data_manager.get_monthly_expenses(username, current_month)
            
            if monthly_expenses > 0 and data_manager.get_budget(username):
                budget = data_manager.get_budget(username)
                if monthly_expenses > budget.total_budget:
                    st.warning(f"Alert! You've exceeded your budget of {budget.total_budget}. Current expenses: {monthly_expenses}")
                else:
                    st.info(f"Your current monthly expenses: {monthly_expenses}. Remaining budget: {budget.total_budget - monthly_expenses}")

            # Export Data
            st.subheader("Export Your Data")
            export_format = st.selectbox("Export Format", ["CSV", "Excel"])
            if st.button("Export"):
                if export_format == "CSV":
                    expense_data.to_csv(f'{username}_expenses.csv')
                    st.success(f"Data exported as {username}_expenses.csv")
                elif export_format == "Excel":
                    expense_data.to_excel(f'{username}_expenses.xlsx')
                    st.success(f"Data exported as {username}_expenses.xlsx")

            # GPT-powered Financial Assistant
            st.header("GPT-powered Financial Assistant")
            st.chat_input("Ask about your expenses:")

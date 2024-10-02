import streamlit as st
import pandas as pd
import plotly.express as px
from forex_python.converter import CurrencyRates
import pytesseract
from PIL import Image
import numpy as np
from sklearn.linear_model import LinearRegression
import random

# Initialize session state for users and expense data
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Currency'])

# User Authentication (Basic)
st.title('Expense Tracker App')

if not st.session_state.user_authenticated:
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        # For simplicity, hardcoded user credentials (can be expanded later)
        if username == "admin" and password == "admin":
            st.session_state.user_authenticated = True
            st.success('Logged in successfully!')
        else:
            st.error('Invalid credentials')

if st.session_state.user_authenticated:

    # Sidebar navigation
    option = st.sidebar.selectbox('Menu', ['Home', 'Add Expense', 'Receipt Scanning', 'Expense Visualization', 
                                           'Currency Conversion', 'Expense Prediction', 'Generate Sample Data'])

    # 1. Home
    if option == 'Home':
        st.header("Welcome to the Expense Tracker App!")
        st.write("""
        This app helps you track your expenses, scan receipts, convert currencies, predict your future expenses,
        and visualize your spending habits.
        """)

    # 2. Add Expense Manually
    if option == 'Add Expense':
        st.header("Add a New Expense")

        # Input form for expenses
        date = st.date_input("Expense Date")
        category = st.selectbox("Expense Category", ["Food", "Travel", "Shopping", "Entertainment", "Health", "Other"])
        amount = st.number_input("Amount")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR", "JPY"])

        if st.button("Add Expense"):
            new_expense = {"Date": date, "Category": category, "Amount": amount, "Currency": currency}
            st.session_state.expenses = st.session_state.expenses.append(new_expense, ignore_index=True)
            st.success(f"Added {category} expense of {amount} {currency}!")

    # 3. Receipt Scanning (OCR using Tesseract)
    if option == 'Receipt Scanning':
        st.header("Receipt Scanning")

        uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Receipt", use_column_width=True)

            # Perform OCR on the image
            receipt_text = pytesseract.image_to_string(img)
            st.text_area("Extracted Text", receipt_text)
            
            # In a real application, add regex to extract date, amount, and category from the receipt text.

    # 4. Expense Visualization (Plotly)
    if option == 'Expense Visualization':
        st.header("Expense Visualization")

        # If there are no expenses, prompt the user to add some.
        if st.session_state.expenses.empty:
            st.warning("No expenses recorded yet. Please add expenses first.")
        else:
            # Visualize the expenses using Plotly
            fig = px.bar(st.session_state.expenses, x="Date", y="Amount", color="Category", barmode="group")
            st.plotly_chart(fig)

    # 5. Currency Conversion (forex-python)
    if option == 'Currency Conversion':
        st.header("Currency Conversion")

        c = CurrencyRates()
        amount = st.number_input("Amount in your local currency (USD)")
        to_currency = st.selectbox("Convert to", ["EUR", "GBP", "INR", "JPY"])

        if st.button("Convert"):
            try:
                converted_amount = c.convert('USD', to_currency, amount)
                st.write(f"Converted Amount: {converted_amount} {to_currency}")
            except Exception as e:
                st.error(f"Error during conversion: {e}")

    # 6. Expense Prediction (Linear Regression)
    if option == 'Expense Prediction':
        st.header("Expense Prediction")

        # Ensure that we have enough data for predictions
        if len(st.session_state.expenses) < 2:
            st.warning("You need at least two expenses to make predictions.")
        else:
            # Create a dummy dataset based on current expenses for prediction
            st.session_state.expenses['Date'] = pd.to_datetime(st.session_state.expenses['Date'])
            st.session_state.expenses.sort_values(by='Date', inplace=True)
            X = np.arange(len(st.session_state.expenses)).reshape(-1, 1)
            y = st.session_state.expenses['Amount'].values

            # Linear Regression for expense prediction
            model = LinearRegression()
            model.fit(X, y)

            # Predict next expense
            next_month = len(X) + 1
            predicted_expense = model.predict([[next_month]])

            st.write(f"Predicted expense for next entry: {predicted_expense[0]:.2f} USD")

            # Alert based on prediction
            budget_limit = st.number_input("Enter your budget limit", value=200.0)
            if predicted_expense[0] > budget_limit:
                st.warning("You are likely to exceed your budget in the next period!")

    # 7. Generate Sample Data
    if option == 'Generate Sample Data':
        st.header("Generate Sample Data")

        def generate_sample_expenses(n=10):
            categories = ["Food", "Travel", "Shopping", "Entertainment", "Health", "Other"]
            data = []
            for i in range(n):
                data.append({
                    "Date": pd.Timestamp('2024-01-01') + pd.DateOffset(days=random.randint(0, 365)),
                    "Category": random.choice(categories),
                    "Amount": random.randint(10, 500),
                    "Currency": random.choice(["USD", "EUR", "GBP"])
                })
            return pd.DataFrame(data)

        if st.button("Generate Sample Data"):
            st.session_state.expenses = generate_sample_expenses()
            st.write(st.session_state.expenses)

    # Display logout button
    if st.sidebar.button('Logout'):
        st.session_state.user_authenticated = False
        st.success("Logged out successfully.")
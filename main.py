import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
from forex_python.converter import CurrencyRates
import base64
import random
import os
from io import BytesIO
from PIL import Image

# ---- Streamlit App Configuration ----
st.set_page_config(page_title="Expense Tracker App", layout="wide")

# ---- Sidebar for Navigation ----
st.sidebar.title("Expense Tracker")
st.sidebar.header("Menu")

# Navigation options
menu = [
    "Dashboard", 
    "Add Expense", 
    "Scan Receipt", 
    "Reports", 
    "Settings", 
    "Investment Tracking", 
    "Goal Tracking", 
    "Budget Alerts", 
    "Generate Sample Data"
]
choice = st.sidebar.selectbox("Navigate", menu)

# ---- Load and Generate Sample Data ----
@st.cache_data
def load_sample_data(currency="USD", period="monthly"):
    np.random.seed(42)
    dates = pd.date_range(datetime.date.today() - pd.DateOffset(months=12), periods=12, freq='M')
    categories = ['Food', 'Transport', 'Bills', 'Rent', 'Entertainment', 'Health', 'Travel']
    data = {
        'Date': dates,
        'Category': [random.choice(categories) for _ in range(12)],
        'Amount': np.random.randint(50, 2000, size=12),
        'Currency': [currency]*12
    }
    df = pd.DataFrame(data)
    return df

def generate_random_data(num_entries=50, currency="USD"):
    np.random.seed(42)
    start_date = datetime.date.today() - pd.DateOffset(months=12)
    end_date = datetime.date.today()
    dates = pd.date_range(start_date, end_date, periods=num_entries)
    categories = ['Food', 'Transport', 'Bills', 'Rent', 'Entertainment', 'Health', 'Travel']
    data = {
        'Date': np.random.choice(dates, num_entries),
        'Category': np.random.choice(categories, num_entries),
        'Amount': np.random.randint(10, 3000, num_entries),
        'Currency': [currency] * num_entries
    }
    return pd.DataFrame(data)

# ---- Currency Conversion Utility ----
def convert_currency(amount, from_currency, to_currency):
    c = CurrencyRates()
    try:
        return c.convert(from_currency, to_currency, amount)
    except Exception as e:
        st.error(f"Currency conversion error: {e}")
        return amount

# ---- File Downloader (for CSV export) ----
def download_file(df, filename="expense_report.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href

# ---- Visualization Function ----
def visualize_expenses(df):
    fig = px.pie(df, names='Category', values='Amount', title="Expenses by Category")
    st.plotly_chart(fig)

# ---- Dashboard ----
if choice == "Dashboard":
    st.title("Expense Dashboard")
    
    # Load or generate sample data
    df = load_sample_data()
    
    # Display data
    st.write("**Expense Summary**")
    st.dataframe(df)
    
    # Visualization
    visualize_expenses(df)
    
    # Total Expense
    st.write(f"**Total Expense**: ${df['Amount'].sum():,.2f}")

# ---- Add Expense ----
elif choice == "Add Expense":
    st.header("Add a New Expense")
    
    with st.form("expense_form"):
        date = st.date_input("Date", value=datetime.date.today())
        category = st.selectbox("Category", ["Food", "Transport", "Bills", "Rent", "Entertainment", "Health", "Travel"])
        amount = st.number_input("Amount", min_value=0.0)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "INR"])
        submit = st.form_submit_button("Add Expense")
    
    if submit:
        # Log and show added expense
        st.write(f"Added Expense: {date}, {category}, {amount:.2f} {currency}")

# ---- Scan Receipt (Stub) ----
elif choice == "Scan Receipt":
    st.header("Scan Receipt for Automatic Expense Entry")
    
    uploaded_file = st.file_uploader("Upload a receipt image (JPG/PNG)", type=["jpg", "png"])
    
    if uploaded_file is not None:
        # Show image and placeholder for OCR processing
        img = Image.open(uploaded_file)
        st.image(img, caption='Uploaded Receipt', use_column_width=True)
        st.write("Processing receipt... (OCR integration goes here)")
        # OCR integration: Implement Tesseract or Google Vision here

# ---- Reports ----
elif choice == "Reports":
    st.header("Expense Reports")
    
    # Filters for generating reports
    report_type = st.selectbox("Report Type", ["Monthly", "Yearly", "Category-Wise"])
    start_date = st.date_input("Start Date", datetime.date.today() - pd.DateOffset(months=1))
    end_date = st.date_input("End Date", datetime.date.today())
    
    # Load and filter data
    df = load_sample_data()
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    st.write(f"Report from {start_date} to {end_date}")
    st.dataframe(filtered_df)
    
    # CSV Download Option
    st.markdown(download_file(filtered_df), unsafe_allow_html=True)

# ---- Settings and Currency Conversion ----
elif choice == "Settings":
    st.header("Settings")
    
    # Currency Conversion Test
    amount = st.number_input("Enter amount to convert")
    from_currency = st.selectbox("From Currency", ["USD", "EUR", "GBP", "INR"])
    to_currency = st.selectbox("To Currency", ["USD", "EUR", "GBP", "INR"])
    
    if st.button("Convert"):
        converted = convert_currency(amount, from_currency, to_currency)
        st.write(f"{amount} {from_currency} = {converted:.2f} {to_currency}")

# ---- Investment Tracking (Stub) ----
elif choice == "Investment Tracking":
    st.header("Track Investments")
    
    # Placeholder for investment tracking and suggestions
    st.write("Track your investments and get recommendations based on your disposable income.")

# ---- Goal Tracking ----
elif choice == "Goal Tracking":
    st.header("Set and Track Financial Goals")
    
    goal = st.text_input("Enter your financial goal (e.g., Save $10,000)")
    current_savings = st.number_input("Current savings amount", min_value=0.0)
    
    if st.button("Track Goal"):
        st.write(f"Goal: {goal}, Current Savings: {current_savings}")

# ---- Budget Alerts ----
elif choice == "Budget Alerts":
    st.header("Budget Alerts")
    
    budget_limit = st.number_input("Set your monthly budget limit", min_value=0.0)
    
    # Load data and check if budget exceeded
    df = load_sample_data()
    total_expense = df['Amount'].sum()
    
    if total_expense > budget_limit:
        st.warning(f"Warning: You've exceeded your budget by ${total_expense - budget_limit:.2f}!")
    else:
        st.success(f"You're within your budget. Total expense: ${total_expense:.2f}")

# ---- Generate Sample Data ----
elif choice == "Generate Sample Data":
    st.header("Generate Random Expense Data")
    
    currency = st.selectbox("Select Currency", ["USD", "EUR", "GBP", "INR", "JPY"])
    num_entries = st.number_input("Number of entries", min_value=10, max_value=1000, step=10)
    
    # Generate and display data
    df = generate_random_data(num_entries, currency)
    st.dataframe(df)
    
    # CSV Download Option
    st.markdown(download_file(df), unsafe_allow_html=True)

# ---- Footer ----
st.sidebar.info("Expense Tracker App © 2024")

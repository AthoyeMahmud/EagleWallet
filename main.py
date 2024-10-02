import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from forex_python.converter import CurrencyRates
import pytesseract
from PIL import Image
import io
import yfinance as yf
import os

# Set page config
st.set_page_config(
    page_title="Expense Tracker", 
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================== App-Wide Utility Functions ========================
def currency_converter(amount, from_currency, to_currency):
    c = CurrencyRates()
    try:
        converted_amount = c.convert(from_currency, to_currency, amount)
        return converted_amount
    except Exception as e:
        st.error(f"Error during currency conversion: {e}")
        return None

def receipt_scanner(image):
    try:
        text = pytesseract.image_to_string(image)
        st.write("Scanned Text from Receipt:")
        st.write(text)
        return text
    except Exception as e:
        st.error(f"Error during receipt scanning: {e}")
        return None

def visualize_expenses(df):
    if df.empty:
        st.write("No data to visualize.")
    else:
        fig = px.pie(df, names='Category', values='Amount', title='Expense Breakdown')
        st.plotly_chart(fig)

def save_to_csv(df, filename="expenses_report.csv"):
    df.to_csv(filename, index=False)
    st.success(f"Data exported successfully as {filename}")

def load_sample_data():
    data = {
        'Date': pd.date_range(start="2023-01-01", periods=12, freq='M'),
        'Category': np.random.choice(['Food', 'Transport', 'Utilities', 'Rent', 'Shopping'], 12),
        'Amount': np.random.randint(50, 300, size=12),
        'Currency': 'USD'
    }
    df = pd.DataFrame(data)
    return df

def stock_recommendations(disposable_income):
    st.write(f"Analyzing stocks for investment with disposable income of: ${disposable_income}")
    # Recommend stocks using yfinance
    stocks = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN']
    stock_data = yf.download(stocks, period='1d')
    st.write(stock_data.tail(1))  # Display the last day's stock data
    st.write("**Recommended Stocks:**")
    st.write(stocks[:3])  # Simplified stock recommendations

# ======================== Sidebar Configuration ========================
st.sidebar.title("Expense Tracker Menu")
option = st.sidebar.selectbox(
    "Choose a feature",
    ['Add Expense', 'Scan Receipt', 'View Expenses', 'Expense Reports', 'Budget Alerts', 'Stock Recommendations']
)

# ======================== Expense Tracker Pages ========================
# Placeholder DataFrame to store all expenses
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Currency'])

# Placeholder for disposable income (random for demo)
if 'disposable_income' not in st.session_state:
    st.session_state['disposable_income'] = 5000  # Random starting point

# ------------------------ Add Expense Page ------------------------
if option == 'Add Expense':
    st.title("Add a New Expense")
    date = st.date_input("Expense Date")
    category = st.selectbox("Category", ['Food', 'Transport', 'Utilities', 'Rent', 'Shopping'])
    amount = st.number_input("Amount")
    currency = st.selectbox("Currency", ['USD', 'EUR', 'GBP', 'JPY'])
    
    if st.button("Add Expense"):
        st.session_state['expenses'] = st.session_state['expenses'].append({
            'Date': date, 'Category': category, 'Amount': amount, 'Currency': currency
        }, ignore_index=True)
        st.success("Expense Added!")

# ------------------------ Scan Receipt Page ------------------------
elif option == 'Scan Receipt':
    st.title("Scan a Receipt")
    uploaded_file = st.file_uploader("Choose a receipt image...", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        scanned_text = receipt_scanner(image)
        if scanned_text:
            st.write("Extracted Data: ", scanned_text)

# ------------------------ View Expenses Page ------------------------
elif option == 'View Expenses':
    st.title("View All Expenses")
    df = st.session_state['expenses']
    
    st.write("Expense Data:")
    st.dataframe(df)
    
    visualize_expenses(df)
    
    # Save or Load Expenses
    if st.button("Export to CSV"):
        save_to_csv(df)

# ------------------------ Expense Reports Page ------------------------
elif option == 'Expense Reports':
    st.title("Generate Expense Reports")
    
    report_type = st.selectbox("Report Type", ['Monthly', 'Yearly'])
    
    df = st.session_state['expenses']
    df['Month'] = pd.to_datetime(df['Date']).dt.month
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    
    if report_type == 'Monthly':
        monthly_report = df.groupby('Month').sum()
        st.write("Monthly Report")
        st.dataframe(monthly_report)
    else:
        yearly_report = df.groupby('Year').sum()
        st.write("Yearly Report")
        st.dataframe(yearly_report)

# ------------------------ Budget Alerts Page ------------------------
elif option == 'Budget Alerts':
    st.title("Set Budget Alerts")
    
    budget_limit = st.number_input("Enter your monthly budget limit:", value=2000)
    current_expenses = st.session_state['expenses']['Amount'].sum()
    
    if current_expenses > budget_limit:
        st.error(f"Alert! You have exceeded your budget limit of ${budget_limit}.")
    else:
        st.success(f"You are within your budget. Current expenses: ${current_expenses}")

# ------------------------ Stock Recommendations Page ------------------------
elif option == 'Stock Recommendations':
    st.title("Stock Recommendations")
    
    disposable_income = st.number_input("Enter your disposable income for investments:", value=st.session_state['disposable_income'])
    stock_recommendations(disposable_income)

# ======================== Footer ========================
st.sidebar.write("© 2024 - Expense Tracker App")


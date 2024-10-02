import streamlit as st
import pandas as pd
import plotly.express as px
from forex_python.converter import CurrencyRates
import pytesseract
from PIL import Image
import numpy as np
from sklearn.linear_model import LinearRegression
import random
import io

# Initialize session state for expenses and goals
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Currency'])
if 'goals' not in st.session_state:
    st.session_state.goals = pd.DataFrame(columns=['Goal', 'Target Amount', 'Current Amount'])

# Function to automatically categorize expenses based on description (you can expand this)
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
        converted_amount = c.convert(from_currency, to_currency, amount)
        return converted_amount
    except:
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
        st.session_state.expenses = st.session_state.expenses.append(new_expense, ignore_index=True)
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
            st.session_state.expenses = st.session_state.expenses.append(new_expense, ignore_index=True)
            st.success(f"Scanned {category} expense of {amount} {currency}!")

elif option == 'Expense Visualization':
    st.header("Expense Visualization")
    if st.session_state.expenses.empty:
        st.warning("No expenses recorded yet. Please add expenses first.")
    else:
        selected_currency = st.selectbox("View expenses in currency", ["USD", "EUR", "GBP", "INR", "JPY"])
        filtered_expenses = st.session_state.expenses.copy()
        for i, row in filtered_expenses.iterrows():
            if row['Currency'] != selected_currency:
                converted = convert_currency(row['Amount'], row['Currency'], selected_currency)
                if converted is not None:
                    filtered_expenses.at[i, 'Amount'] = converted
                    filtered_expenses.at[i, 'Currency'] = selected_currency
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
        st.session_state.goals = st.session_state.goals.append(new_goal, ignore_index=True)
        st.success(f"Added goal '{goal_name}' with a target of {target_amount}!")

elif option == 'Expense Prediction':
    st.header("Expense Prediction")
    if len(st.session_state.expenses) < 2:
        st.warning("You need at least two expenses to make predictions.")
    else:
        st.session_state.expenses['Date'] = pd.to_datetime(st.session_state.expenses['Date'])
        st.session_state.expenses.sort_values(by='Date', inplace=True)
        X = np.arange(len(st.session_state.expenses)).reshape(-1, 1)
        y = st.session_state.expenses['Amount'].values
        model = LinearRegression()
        model.fit(X, y)
        next_month = len(X) + 1
        predicted_expense = model.predict([[next_month]])
        st.write(f"Predicted expense for next entry: {predicted_expense[0]:.2f} USD")
        budget_limit = st.number_input("Enter your budget limit", value=200.0)
        if predicted_expense[0] > budget_limit:
            st.warning(f"You are likely to exceed your budget of {budget_limit} in the next period!")

elif option == 'Travel Budgeting':
    st.header("Travel/Vacation Budgeting")
    trip_name = st.text_input("Trip Name")
    travel_goal = st.number_input("Total Trip Budget")
    trip_expenses = st.number_input("Current Trip Expenses", min_value=0.0)
    remaining_budget = travel_goal - trip_expenses
    st.write(f"Remaining travel budget for {trip_name}: {remaining_budget:.2f}")

elif option == 'Debt Tracking':
    st.header("Debt Tracking and Payoff Strategies")
    debt_name = st.text_input("Debt Name (e.g., Car loan, Mortgage)")
    total_debt = st.number_input("Total Debt Amount")
    monthly_payment = st.number_input("Monthly Payment")
    months_to_payoff = total_debt / monthly_payment if monthly_payment > 0 else 0
    st.write(f"It will take you {months_to_payoff:.2f} months to pay off {debt_name}.")

elif option == 'Generate Sample Data':
    st.header("Generate Sample Data")
    def generate_sample_expenses(n=10):
        categories = ["Food", "Travel", "Shopping", "Entertainment", "Health", "Other"]
        data = []
        for i in range(n):
            data.append({
                "Date": pd.Timestamp('2024-01-01') + pd.DateOffset(days=random.randint(0, 365)),
                "Category": random.choice(categories),
                "Description": "Sample expense",
                "Amount": random.randint(10, 500),
                "Currency": random.choice(["USD", "EUR", "GBP", "INR", "JPY"])
            })
        return pd.DataFrame(data)

    if st.button("Generate Sample Data"):
        st.session_state.expenses = generate_sample_expenses()
        st.write(st.session_state.expenses)

elif option == 'Import/Export':
    st.header("Import/Export Expense Data")
    if st.session_state.expenses.empty:
        st.warning("No expenses to export. Please add expenses first.")
    else:
        csv = st.session_state.expenses.to_csv(index=False)
        st.download_button(
            label="Export Expenses to CSV",
            data=csv,
            file_name='expenses.csv',
            mime='text/csv',
        )

    st.subheader("Import Expenses from CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        imported_expenses = pd.read_csv(uploaded_file)
        st.session_state.expenses = pd.concat([st.session_state.expenses, imported_expenses], ignore_index=True)
        st.success("Expenses imported successfully!")
        st.write(st.session_state.expenses)
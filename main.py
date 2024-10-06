import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random
from sklearn.linear_model import LinearRegression
import numpy as np

# Centralized session state initialization
def initialize_session_state():
    state_defaults = {"expense_data": [], "debts": []}
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

def generate_sample_data(currency="USD", period="week"):
    periods = {"day": 1, "week": 7, "month": 30, "year": 365, "decade": 3650}
    num_days = periods.get(period.lower(), 7)  # Default to 7 days
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=num_days)
    date_range = pd.date_range(start=start_date, end=end_date)

    categories = ["Groceries", "Dining", "Travel", "Utilities", "Entertainment", "Shopping"]
    data = [
        {"Date": date, "Category": random.choice(categories), "Amount": round(random.uniform(5, 500), 2), "Currency": currency}
        for date in date_range
    ]
    return data

def add_expense():
    with st.form("add_expense_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Groceries", "Dining", "Travel", "Utilities", "Entertainment", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", ...])
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("Add Expense")
        if submitted and amount > 0:
            expense = {"Date": date, "Category": category, "Amount": amount, "Currency": currency, "Description": description}
            st.session_state.expense_data.append(expense)
            st.success("Expense added!")
        else:
            st.warning("Please enter a valid amount.")

def view_expenses():
    df = pd.DataFrame(st.session_state.expense_data)
    if not df.empty:
        st.write("Expenses Table:")
        st.dataframe(df)

        df['Date'] = pd.to_datetime(df['Date'])
        daily_expenses = df.groupby('Date')['Amount'].sum()
        date_fig = px.line(daily_expenses, x=daily_expenses.index, y='Amount', title="Daily Expense Trend")
        st.plotly_chart(date_fig)

        category_fig = px.bar(df, x='Category', y='Amount', color='Currency', title='Expenses by Category')
        st.plotly_chart(category_fig)

        csv = df.to_csv(index=False)
        st.download_button("Download as CSV", data=csv, file_name="expenses.csv", mime="text/csv")
    else:
        st.warning("No data available.")

def track_debts():
    with st.form("debt_form"):
        debt_name = st.text_input("Debt Name")
        total_amount = st.number_input("Total Amount", min_value=0.0, step=0.01)
        interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, step=0.01)
        minimum_payment = st.number_input("Minimum Monthly Payment", min_value=0.0, step=0.01)
        submitted_debt = st.form_submit_button("Add Debt")
        if submitted_debt:
            st.session_state.debts.append({"Debt Name": debt_name, "Total Amount": total_amount, "Interest Rate": interest_rate, "Minimum Payment": minimum_payment})
            st.success("Debt added!")
    
    debts_df = pd.DataFrame(st.session_state.debts)
    if not debts_df.empty:
        st.write("Current Debts:")
        st.dataframe(debts_df)
    else:
        st.write("No debts tracked yet.")

def predict_expenses():
    expenses_df = pd.DataFrame(st.session_state.expense_data)
    if len(expenses_df) < 5:
        st.warning("Not enough expense data for predictions. At least 5 data points are required.")
        return

    expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
    expenses_df['Days'] = (expenses_df['Date'] - expenses_df['Date'].min()).dt.days

    X = expenses_df['Days'].values.reshape(-1, 1)
    y = expenses_df['Amount'].values

    model = LinearRegression()
    try:
        model.fit(X, y)
        future_days = np.arange(expenses_df['Days'].max(), expenses_df['Days'].max() + 31).reshape(-1, 1)
        predicted_amount = model.predict(future_days)

        fig = px.line(x=future_days.flatten(), y=predicted_amount, title="30-Day Expense Prediction", labels={'x': 'Days from Start', 'y': 'Predicted Amount'})
        fig.add_scatter(x=expenses_df['Days'], y=expenses_df['Amount'], mode='markers', name="Actual Expenses")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Prediction failed: {e}")

def main():
    st.title("Expense Tracker")
    menu = ["Add Expense", "View Expenses", "Track Debts", "Predict Expenses", "Generate Sample Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Expense":
        add_expense()
    elif choice == "View Expenses":
        view_expenses()
    elif choice == "Track Debts":
        track_debts()
    elif choice == "Predict Expenses":
        predict_expenses()
    elif choice == "Generate Sample Data":
        with st.form("generate_data_form"):
            currency_sample = st.selectbox("Select Currency for Sample Data", ["USD", "EUR", "GBP"])
            period_sample = st.selectbox("Sample Data Time Period", ["Day", "Week", "Month", "Year", "Decade"])
            submitted_generate = st.form_submit_button("Generate Sample Data")
            if submitted_generate:
                st.session_state.expense_data = generate_sample_data(currency=currency_sample, period=period_sample)
                st.success("Sample data generated!")

if __name__ == "__main__":
    main()

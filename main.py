import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random

# Sample data generation (single currency for now)
def generate_sample_data(currency="USD", period="week"):
    num_days = 7 # default 1 week
    if period.lower() == "day": num_days = 1
    elif period.lower() == "month": num_days = 30
    elif period.lower() == "year": num_days = 365
    elif period.lower() == "decade": num_days = 3650
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=num_days)
    date_range = pd.date_range(start=start_date, end=end_date)

    categories = ["Groceries", "Dining", "Travel", "Utilities", "Entertainment", "Shopping"]
    data = []
    for date in date_range:
        category = random.choice(categories)
        amount = round(random.uniform(5, 500), 2)  # Adjust range as needed
        data.append({"Date": date.strftime('%Y-%m-%d'), "Category": category, "Amount": amount, "Currency": currency})
    return data

# Placeholder for expense data (replace with database integration)
if "expense_data" not in st.session_state:
    st.session_state.expense_data = []

# Add Expense
def add_expense():
    with st.form("add_expense_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Groceries", "Dining", "Travel", "Utilities", "Entertainment", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01) # allow cents/pennies
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "HKD", "INR", "KRW", "MXN", "NZD", "SGD", "ZAR"])  # more currencies
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            st.session_state.expense_data.append({"Date": date.strftime('%Y-%m-%d'), "Category": category, "Amount": amount, "Currency": currency, "Description": description})
            st.success("Expense added!")


# View Expenses
def view_expenses():
    df = pd.DataFrame(st.session_state.expense_data)
    if not df.empty:
        st.write("Expenses Table:")
        st.dataframe(df)
        
        # Expense Visualization (Plotly)
        currency_counts = df.groupby('Currency')['Amount'].sum()
        currency_fig = px.pie(currency_counts, values='Amount', names=currency_counts.index, title='Expenses by Currency')
        st.plotly_chart(currency_fig)
        
        # Assuming Date is formatted as 'YYYY-MM-DD'
        df['Date'] = pd.to_datetime(df['Date'])
        daily_expenses = df.groupby('Date')['Amount'].sum()

        date_fig = px.line(daily_expenses, x=daily_expenses.index, y='Amount', title="Daily Expense Trend")
        st.plotly_chart(date_fig)
        
        category_fig = px.bar(df, x='Category', y='Amount', color='Currency', title='Expenses by Category')
        st.plotly_chart(category_fig)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button("Download as CSV", data=csv, file_name="expenses.csv", mime="text/csv")


    else:
        st.warning("No data available.")


# Main Streamlit App
def main():
    st.title("Expense Tracker")

    menu = ["Add Expense", "View Expenses", "Generate Sample Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Expense":
        add_expense()
    elif choice == "View Expenses":
        view_expenses()
    elif choice == "Generate Sample Data":
        with st.form("generate_data_form"):
            currency_sample = st.selectbox("Select Currency for Sample Data", ["USD", "EUR", "GBP"])  # More currency options
            period_sample = st.selectbox("Sample Data Time Period", ["Day", "Week", "Month", "Year", "Decade"])
            submitted_generate = st.form_submit_button("Generate Sample Data")
            if submitted_generate:
                st.session_state.expense_data = generate_sample_data(currency=currency_sample, period=period_sample)
                st.success("Sample data generated!")


# Debt Tracking
def track_debts():
    if "debts" not in st.session_state:
        st.session_state.debts = []

    with st.form("debt_form"):
        debt_name = st.text_input("Debt Name (e.g., Credit Card, Loan)")
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
        # ... (Debt repayment strategies, visualizations can be added here later)
    else:
        st.write("No debts tracked yet.")

# Predictions (Basic Linear Regression)

def predict_expenses():
    expenses_df = pd.DataFrame(st.session_state.expense_data)
    if expenses_df.empty or len(expenses_df) < 5:  # Need enough data for basic prediction
        st.warning("Not enough expense data for predictions. At least 5 data points are required.")
        return

    expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
    expenses_df['Days'] = (expenses_df['Date'] - expenses_df['Date'].min()).dt.days

    X = expenses_df['Days'].values.reshape(-1, 1)  # Use days as predictor
    y = expenses_df['Amount'].values

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.array([i for i in range(expenses_df['Days'].max(), expenses_df['Days'].max() + 31)]).reshape(-1, 1)
    predicted_amount = model.predict(future_days)


    # Visualization using Plotly
    fig = px.line(x=future_days.flatten(), y=predicted_amount, title="30-Day Expense Prediction (Linear Regression)", labels={'x': 'Days from First Recorded Expense', 'y': 'Predicted Amount'})

    fig.add_scatter(x=expenses_df['Days'], y=expenses_df['Amount'], mode='markers', name="Actual Expenses")
    st.plotly_chart(fig)


def main():
    st.title("Expense Tracker")

    menu = ["Add Expense", "View Expenses", "Track Debts", "Predict Expenses", "Generate Sample Data"] # Added "Track Debts" and "Predict Expenses"
    choice = st.sidebar.selectbox("Menu", menu)


    if choice == "Add Expense":
        add_expense()  # Currency and description are already included.
    elif choice == "View Expenses":
        view_expenses()
    elif choice == "Track Debts":
        track_debts()
    elif choice == "Predict Expenses":
        predict_expenses()
    elif choice == "Generate Sample Data":
       # ... (generate sample data remains same)


if __name__ == "__main__":
    main()
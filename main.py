import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random
from sklearn.linear_model import LinearRegression
import numpy as np
import requests
import yfinance as yf

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
    st.subheader("Add Expense")
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

def add_income():
    st.subheader("Add Income")
    with st.form("add_income_form"):
        date = st.date_input("Date", key="income_date")
        source = st.text_input("Income Source")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, key="income_amount")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "BDT", "Other"], key="income_currency")
        description = st.text_input("Description (optional)", key="income_description")
        submitted = st.form_submit_button("Add Income")
        if submitted and amount > 0:
            income = {"Date": date, "Source": source, "Amount": amount, "Currency": currency, "Description": description}
            if 'income_data' not in st.session_state:
                st.session_state['income_data'] = []
            st.session_state.income_data.append(income)
            st.success("Income added!")

def view_incomes():
    st.subheader("View Incomes")
    if 'income_data' in st.session_state and st.session_state.income_data:
        df_income = pd.DataFrame(st.session_state.income_data)
        st.dataframe(df_income)
    else:
        st.warning("No income data available.")

def view_expenses():
    st.subheader("View Expenses")
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

def expense_heatmap():
    st.subheader("Expense Heatmap")

    if st.session_state.expense_data:
        df = pd.DataFrame(st.session_state.expense_data)
        df['Date'] = pd.to_datetime(df['Date'])

        heatmap_data = df.pivot_table(index=df['Date'].dt.date, columns='Category', values='Amount', aggfunc='sum', fill_value=0)

        fig = px.imshow(heatmap_data.T, color_continuous_scale='Viridis', 
                        title="Expense Heatmap by Category", labels=dict(x="Date", y="Category", color="Amount"))
        st.plotly_chart(fig)
    else:
        st.warning("No expense data available for heatmap.")

def add_recurring_transaction():
    st.subheader("Add Recurring Transaction")
    with st.form("recurring_transaction_form"):
        transaction_type = st.selectbox("Type", ["Expense", "Income"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        category_or_source = st.text_input("Category or Source")
        recurrence_interval = st.selectbox("Recurrence Interval", ["Weekly", "Monthly"])
        start_date = st.date_input("Start Date")
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("Add Recurring Transaction")

        if submitted:
            transaction = {
                "Type": transaction_type,
                "Amount": amount,
                "Category_or_Source": category_or_source,
                "Recurrence": recurrence_interval,
                "Start Date": start_date,
                "Description": description
            }
            if 'recurring_transactions' not in st.session_state:
                st.session_state['recurring_transactions'] = []
            st.session_state.recurring_transactions.append(transaction)
            st.success(f"Recurring {transaction_type.lower()} added!")

    # Display existing recurring transactions
    if 'recurring_transactions' in st.session_state:
        st.write("Recurring Transactions")
        df_recurring = pd.DataFrame(st.session_state.recurring_transactions)
        st.dataframe(df_recurring)

def track_debts():
    st.subheader("Track Debts")
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

def budget_planning():
    st.subheader("Budget Planning")
    with st.form("budget_form"):
        categories = ["Groceries", "Dining", "Travel", "Utilities", "Entertainment", "Shopping"]
        budget_data = {cat: st.number_input(f"Budget for {cat}", min_value=0.0, step=0.01) for cat in categories}
        submitted_budget = st.form_submit_button("Set Budget")
        if submitted_budget:
            st.session_state.budget = budget_data
            st.success("Budgets set!")

    # Compare expenses to budget
    if "expense_data" in st.session_state and st.session_state.expense_data:
        df = pd.DataFrame(st.session_state.expense_data)
        category_expenses = df.groupby("Category")["Amount"].sum()
        if "budget" in st.session_state:
            budget = pd.Series(st.session_state.budget)
            comparison = pd.DataFrame({"Spent": category_expenses, "Budget": budget})
            st.write("Budget vs Actual Expenses")
            st.dataframe(comparison.fillna(0))

def savings_goals():
    st.subheader("Savings Goals")
    with st.form("savings_goal_form"):
        goal_name = st.text_input("Goal Name")
        target_amount = st.number_input("Target Amount", min_value=0.0, step=0.01)
        current_savings = st.number_input("Current Savings", min_value=0.0, step=0.01)
        submitted_goal = st.form_submit_button("Add Savings Goal")
        if submitted_goal:
            goal = {"Goal Name": goal_name, "Target Amount": target_amount, "Current Savings": current_savings}
            if 'savings_goals' not in st.session_state:
                st.session_state['savings_goals'] = []
            st.session_state.savings_goals.append(goal)
            st.success("Savings Goal added!")

    # Display savings goals and progress
    if 'savings_goals' in st.session_state:
        df_savings = pd.DataFrame(st.session_state.savings_goals)
        df_savings['Progress (%)'] = (df_savings['Current Savings'] / df_savings['Target Amount']) * 100
        st.write("Savings Goals Progress")
        st.dataframe(df_savings)

def predict_expenses():
    st.subheader("Predict Expenses")
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

def upload_csv():
    st.subheader("Import CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("CSV Data:")
        st.dataframe(df)
        
        st.subheader("Export CSV")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name='exported_data.csv', mime='text/csv')

def live_currency_rates():
    st.subheader("Live Currency Exchange Rates (BDT)")
    
    currency_pairs = {
        "USD/BDT": "USD/BDT",
        "EUR/BDT": "EUR/BDT",
        "GBP/BDT": "GBP/BDT",
        "AUD/BDT": "AUD/BDT",
        "CAD/BDT": "CAD/BDT",
        "JPY/BDT": "JPY/BDT",
        "CHF/BDT": "CHF/BDT",
        "INR/BDT": "INR/BDT",
        "CNY/BDT": "CNY/BDT",
        "NZD/BDT": "NZD/BDT",
        "SGD/BDT": "SGD/BDT",
        "HKD/BDT": "HKD/BDT",
    }

    currency_data = {}
    for pair in currency_pairs:
        try:
            ticker = yf.Ticker(pair.split("/")[0] + pair.split("/")[1] + "=X")
            price = ticker.history(period="1d")["Close"].iloc[-1]
            currency_data[pair] = price
        except Exception as e:
            currency_data[pair] = f"Error: {str(e)}"

    # Creating a DataFrame to display the results
    df_currency = pd.DataFrame(list(currency_data.items()), columns=["Currency Pair", "Exchange Rate (BDT)"])
    st.table(df_currency)


def live_stock_prices():
    st.subheader("Live Stocks - Fortune 500")

    # List of Fortune 500 stock tickers (sample for illustration, can be expanded)
    stock_tickers = [
        "AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "JPM", "V", "PG", "JNJ", "UNH", "VZ", "WMT", "CVX", "XOM", 
        "KO", "PEP", "CSCO", "HD", "DIS", "MA", "BA", "MCD", "IBM", "NFLX", "NKE"
        # Add more tickers as needed
    ]

    stock_data = {}
    for ticker in stock_tickers:
        try:
            stock = yf.Ticker(ticker)
            stock_data[ticker] = stock.history(period="1d")["Close"].iloc[-1]
        except Exception as e:
            stock_data[ticker] = f"Error: {str(e)}"

    # Create DataFrame with stock tickers and prices
    stock_df = pd.DataFrame.from_dict(stock_data, orient="index", columns=["Price (USD)"])
    stock_df.index.name = "Company Ticker"

    # Display the stock data as a table
    st.table(stock_df)

def dashboard():
    st.title("EagleWallet Dashboard")
    
    # Overview Metrics
    st.header("Financial Overview")
    col1, col2, col3 = st.columns(3)
    
    income_data = st.session_state.get('income_data', [])
    expense_data = st.session_state.get('expense_data', [])
    
    total_income = sum([income['Amount'] for income in income_data])
    total_expense = sum([expense['Amount'] for expense in expense_data])
    savings = total_income - total_expense
    
    with col1:
        st.metric(label="Total Income", value=f"${total_income:,.2f}")
    with col2:
        st.metric(label="Total Expenses", value=f"${total_expense:,.2f}")
    with col3:
        st.metric(label="Net Savings", value=f"${savings:,.2f}")
    
    # Income and Expense Trend Chart
    st.header("Income & Expenses Over Time")
    if income_data and expense_data:
        df_income = pd.DataFrame(income_data)
        df_expense = pd.DataFrame(expense_data)
        
        if not df_income.empty and not df_expense.empty:
            df_income['Date'] = pd.to_datetime(df_income['Date'])
            df_expense['Date'] = pd.to_datetime(df_expense['Date'])

            # Aggregating data
            daily_income = df_income.groupby('Date')['Amount'].sum().reset_index(name='Income')
            daily_expense = df_expense.groupby('Date')['Amount'].sum().reset_index(name='Expense')

            # Merging income and expense data
            df_finances = pd.merge(daily_income, daily_expense, on='Date', how='outer').fillna(0)

            # Plotting
            fig = px.line(df_finances, x='Date', y=['Income', 'Expense'], labels={"value": "Amount", "variable": "Type"})
            st.plotly_chart(fig)
    
    # Expense Category Breakdown
    st.header("Expense Breakdown by Category")
    if expense_data:
        df_expense['Date'] = pd.to_datetime(df_expense['Date'])
        category_fig = px.pie(df_expense, names='Category', values='Amount', title='Expenses by Category')
        st.plotly_chart(category_fig)

    # Budget Comparison
    budget = st.session_state.get('budget', {})
    if budget:
        st.header("Budget vs Actual Spending")
        category_expenses = df_expense.groupby("Category")["Amount"].sum()
        budget_series = pd.Series(budget)

        # Align budget and actual expenses
        comparison = pd.DataFrame({"Spent": category_expenses, "Budget": budget_series}).fillna(0)

        # Plotting the comparison
        budget_fig = px.bar(comparison, x=comparison.index, y=["Spent", "Budget"], barmode='group', title="Budget vs Actual")
        st.plotly_chart(budget_fig)

    # Savings Goals Progress
    savings_goals = st.session_state.get('savings_goals', [])
    if savings_goals:
        st.header("Savings Goals Progress")
        df_savings = pd.DataFrame(savings_goals)
        df_savings['Progress (%)'] = (df_savings['Current Savings'] / df_savings['Target Amount']) * 100

        # Plot savings progress
        savings_fig = px.bar(df_savings, x='Goal Name', y='Progress (%)', title="Savings Progress", range_y=[0, 100])
        st.plotly_chart(savings_fig)

#Interface and navigation
def main():
    st.title("EagleWallet")

    # Sidebar Menu using st.radio for navigation
    menu = ["Wallet Dashboard","Add Income","View Incomes","Add Expense", "View Expenses","Expense Heatmap","Add Recurring Transaction", "Track Debts","Budget Planning" ,"Savings Goals" , "Predict Expenses", "Generate Sample Data", "Import/Export CSV", "Live Currency Rates", "Stocks"]
    choice = st.sidebar.radio("Menu", menu)

    # Show appropriate content based on the user's selection
    if choice == "EagleWallet Dashboard":
        dashboard()
    elif choice == "Add Income":
        add_income()
    elif choice == "View Incomes":
        view_incomes()
    elif choice == "Add Expense":
        add_expense()
    elif choice == "View Expenses":
        view_expenses()
    elif choice == "Expense Heatmap":
        expense_heatmap()
    elif choice == "Add Recurring Transaction":
        add_recurring_transaction()
    elif choice == "Track Debts":
        track_debts()
    elif choice == "Budget Planning":
        budget_planning()
    elif choice == "Savings Goals":
        savings_goals()
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
    elif choice == "Import/Export CSV":
        upload_csv()
    elif choice == "Currency Rates":
        live_currency_rates()
    elif choice == "Stocks":
        live_stock_prices()              

    # Team member names at the bottom of the sidebar
    st.sidebar.markdown("---")  # Separator line
    st.sidebar.write("Project by:")
    st.sidebar.write("Code Economists")
    st.sidebar.write("• Suhrab")
    st.sidebar.write("• Mashuk")
    st.sidebar.write("• Athoye")

if __name__ == "__main__":
    main()
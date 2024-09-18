import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ExpenseTracker:
    def __init__(self, budget_limit=1000):
        """Initialize the expense tracker with a budget limit."""
        if 'expenses' not in st.session_state:
            st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        self._budget_limit = budget_limit

    @property
    def budget_limit(self):
        return self._budget_limit

    @budget_limit.setter
    def budget_limit(self, value):
        if value > 0:
            self._budget_limit = value
        else:
            raise ValueError("Budget limit must be a positive value")

    def add_expense(self, date, category, amount, description):
        """Add a new expense to the tracker."""
        new_expense = pd.DataFrame([[date, category, amount, description]],
                                   columns=st.session_state.expenses.columns)
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

    def save_expenses(self):
        """Save the current expenses to a CSV file."""
        st.session_state.expenses.to_csv('expenses.csv', index=False)
        st.success("Expenses saved successfully!")

    def load_expenses(self):
        """Load expenses from a CSV file."""
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file:
            st.session_state.expenses = pd.read_csv(uploaded_file)
            st.success("Expenses loaded successfully!")

    def visualize_expenses(self):
        """Visualize the expenses as a bar chart."""
        if not st.session_state.expenses.empty:
            fig, ax = plt.subplots()
            sns.barplot(data=st.session_state.expenses, x='Category', y='Amount', ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.warning("No expenses to visualize!")

    def budget_alert(self):
        """Check if the budget is exceeded and alert the user."""
        total_expenses = st.session_state.expenses['Amount'].sum()
        if total_expenses > self._budget_limit:
            st.error(f"Warning! You've exceeded your budget of {self._budget_limit}!")
        else:
            st.success(f"You're within your budget of {self._budget_limit}.")

    def export_data(self):
        """Allow the user to export expense data as a CSV."""
        st.download_button(
            label="Download data as CSV",
            data=st.session_state.expenses.to_csv().encode('utf-8'),
            file_name='expenses.csv',
            mime='text/csv'
        )

    def predict_expenses(self):
        """Predict future expenses based on current data (simple model)."""
        if not st.session_state.expenses.empty:
            prediction = st.session_state.expenses['Amount'].sum() * 1.1  # Increase by 10%
            st.write(f"Predicted expenses for the next period: {prediction:.2f}")
        else:
            st.warning("No data available for prediction.")

def main():
    tracker = ExpenseTracker()

    st.title("Expense Tracker App")

    # Sidebar for adding expenses and setting budget
    with st.sidebar:
        st.header('Add Expense')
        date = st.date_input("Date")
        category = st.selectbox('Category', ['Food', 'Transport', 'Entertainment', 'Utilities', 'Other'])
        amount = st.number_input('Amount', min_value=0.0, format="%.2f")
        description = st.text_input('Description')
        if st.button('Add'):
            tracker.add_expense(date, category, amount, description)
            st.success("Expense added!")

        st.header("Budget Settings")
        budget_limit = st.number_input("Set your budget limit", min_value=0.0, value=tracker.budget_limit)
        tracker.budget_limit = budget_limit

        st.header("File Operations")
        if st.button('Save Expenses'):
            tracker.save_expenses()
        if st.button('Load Expenses'):
            tracker.load_expenses()

    st.header("Expense Data")
    st.write(st.session_state.expenses)

    st.header("Expense Visualization")
    if st.button('Visualize Expenses'):
        tracker.visualize_expenses()

    st.header("Budget Alerts")
    if st.button('Check Budget'):
        tracker.budget_alert()

    st.header("Expense Predictions")
    if st.button('Predict Expenses'):
        tracker.predict_expenses()

    st.header("Data Export")
    tracker.export_data()

if __name__ == "__main__":
    main()

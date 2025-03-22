import sqlite3
import pandas as pd
import random
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from faker import Faker
from datetime import date

# Initialize Faker
fake = Faker()

# Define Categories and Payment Modes
Categories = ['Groceries', 'Utilities', 'Rent', 'Entertainment', 'Insurance', 'Travel', 'Subscription']
Payment_mode = ['Paytm', 'Gpay', 'Credit_card', 'Debit_card', 'Cash', 'Paypal', 'Check', 'Bank_transfer', 'Visa']

# Define Descriptions
Description = {
    'Groceries': "Monthly groceries",
    'Utilities': ['Electricity bill', 'Water bill', 'Internet bill'],
    'Rent': ["Monthly house rent"],
    'Entertainment': ['Went to movies', 'Tour', 'Day off'],
    'Insurance': ['Life', 'Car'],
    'Travel': ['Flight','Accommodation','Transportation'],
    'Subscription': ['Netflix', 'Amazon Prime']
}

# Function to generate random expense data
def get_expense(entries, start_date, end_date):
    values = []
    for _ in range(entries):
        amount = round(random.uniform(1000, 10000), 2)
        category = random.choice(Categories)

        # Choose description correctly
        if isinstance(Description[category], list):
            description = random.choice(Description[category])
        else:
            description = Description[category]

        expenses = (
            fake.date_between(start_date=start_date, end_date=end_date),
            category,
            random.choice(Payment_mode),
            description,
            amount,
            round(random.uniform(0, 0.1) * amount, 2)
        )
        values.append(expenses)
    return values

# SQLite Database Setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Create Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Expense_Table (
                    DATE DATE ,
                    CATEGORIES TEXT, 
                    PAYMENT_MODE TEXT, 
                    DESCRIPTION TEXT, 
                    AMOUNTS REAL, 
                    CASHBACK REAL)''')

conn.commit()

# Streamlit UI
st.title("💰 Expense Tracker")

# Sidebar Menu
option = st.sidebar.radio("Select an option", ["Add Expenses", "View & Analyze"])

# Option 1: Add Expenses
if option == "Add Expenses":
    st.subheader("📌 Generate and Store Random Expenses")

    entries = st.number_input("Enter number of expenses:", min_value=1, max_value=1000, value=10)
    if st.button("Generate & Store"):
        expenses = get_expense(entries, date(2024, 1, 1), date(2024, 12, 31))
        cursor.executemany("INSERT INTO Expense_Table VALUES (?,?,?,?,?,?)", expenses)
        conn.commit()
        st.success(f"{entries} expenses added successfully!")

# Option 2: View & Analyze
elif option == "View & Analyze":
    st.subheader("📊 Expense Analysis")

    # Fetch data from SQLite
    df = pd.read_sql("SELECT * FROM Expense_Table", conn)

    if df.empty:
        st.warning("No expenses found! Please add some data.")
    else:
        st.dataframe(df)

        # **1. Total Expense by Category**
        st.subheader("💼 Total Expense by Category")
        category_expense = df.groupby("CATEGORIES")["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x="AMOUNTS", y="CATEGORIES", data=category_expense, ax=ax)
        ax.set_title("Total Expense by Category")
        st.pyplot(fig)

        # **2. Total Expense by Payment Mode**
        st.subheader("💳 Total Expense by Payment Mode")
        payment_expense = df.groupby("PAYMENT_MODE")["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x="AMOUNTS", y="PAYMENT_MODE", data=payment_expense, ax=ax)
        ax.set_title("Total Expense by Payment Mode")
        st.pyplot(fig)

        # **3. Total Cashback by Category**
        st.subheader("💰 Total Cashback by Category")
        cashback_data = df.groupby("CATEGORIES")["CASHBACK"].sum().reset_index()
        fig, ax = plt.subplots()
        sns.barplot(x="CASHBACK", y="CATEGORIES", data=cashback_data, ax=ax, palette="viridis")
        ax.set_title("Total Cashback by Category", fontsize=14)
        ax.set_xlabel("Total Cashback ($)")
        ax.set_ylabel("Category")
        st.pyplot(fig)

        # **4. Top 5 Most Expensive Categories**
        st.subheader("💰 Top 5 Most Expensive Categories")
        expensive_categories = df.groupby("CATEGORIES")["AMOUNTS"].sum().reset_index()
        expensive_categories = expensive_categories.sort_values(by="AMOUNTS", ascending=False).head(5)
        st.write("Top 5 Expensive Categories Data:", expensive_categories)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="AMOUNTS", y="CATEGORIES", data=expensive_categories, ax=ax, palette="magma")
        ax.set_title("Top 5 Most Expensive Categories", fontsize=14)
        ax.set_xlabel("AMOUNTS ($)")
        ax.set_ylabel("Categories")
        st.pyplot(fig)

        # **5. Spent on transportation using different payment modes
        st.subheader("🚗 Total Spent on Travel by Payment Mode")
        Travel_Data =df.groupby("PAYMENT_MODE")["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(x="AMOUNTS", y="PAYMENT_MODE", data= Travel_Data, palette="coolwarm", ax=ax)
        ax.set_title("AMOUNTS on Travel by PAYMENT_MODE", fontsize=14)
        ax.set_xlabel("AMOUNTS ($)")
        ax.set_ylabel("PAYMENT_MODE")
        st.pyplot(fig)

        # **6. Transactions resulted in cashback
        st.subheader("💰 Transactions with Cashback")
        cashback_df = df[df["CASHBACK"] > 0]
        if not cashback_df.empty:
         fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(cashback_df["CASHBACK"], bins=10, kde=True, color="purple", ax=ax)
        ax.set_title("Distribution of Cashback Amounts", fontsize=14)
        ax.set_xlabel("Cashback Amount ($)")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # **7. The total spending in each month of the year
        st.subheader("📅 Monthly Spending Trends")
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["MONTH"] = df["DATE"].dt.strftime("%Y-%m")
        monthly_data = df.groupby("MONTH")["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.plot(monthly_data["MONTH"], monthly_data["AMOUNTS"], marker="o", linestyle="-", color="b")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Spent ($)")
        ax.set_title("Total Spending Per Month")
        plt.xticks(rotation=45) 
        st.pyplot(fig) 

        # **8 Highest Spending Months in Travel, Entertainment, or Gifts
        st.subheader("📅 Highest Spending Months in Travel, Entertainment, or Gifts")
        selected_categories = ["Travel", "Entertainment", "Gifts"]
        monthly_spending = df.groupby(["MONTH", "CATEGORIES"])["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x="MONTH", y="AMOUNTS", hue="CATEGORIES", data=monthly_spending, ax=ax)
        ax.set_title("Highest Spending Months for Travel, Entertainment, or Gifts", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Spent ($)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

       # **9 # Cashback or rewards were earned in each month
        st.subheader("💰 Cashback Earned Each Month")
        Cashback_by_month = df.groupby("MONTH")["CASHBACK"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=Cashback_by_month, x="MONTH", y="CASHBACK", marker="o", color="green", ax=ax)
        ax.set_title("Cashback Earned Over Time", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Cashback ($)")
        plt.xticks(rotation=45)  # Rotate x-axis for better readability
        st.pyplot(fig)

        # **10 Overall spending changed over time (e.g., increasing, decreasing, remaining stable)
        st.subheader("Overall spending changed over time (e.g., increasing, decreasing, remaining stable)")
        monthly_spending = df.groupby(df["DATE"].dt.to_period("M"))["AMOUNTS"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(x=monthly_spending["DATE"].astype(str), y=monthly_spending["AMOUNTS"], marker="o", color="b")
        ax.set_title("Total Spending Over Time", fontsize=14)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Total Spending ($)", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)  
        st.pyplot(fig)

        # **11 Which Categories have the most number of transactions
        st.subheader("📊 Categories have the most number of transactions")
        category_counts = df["CATEGORIES"].value_counts().reset_index()
        category_counts.columns = ["Categories", "Transaction Count"]
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="Transaction Count", y="Categories", data=category_counts, palette="coolwarm", ax=ax)
        ax.set_title("Number of Transactions by Categories", fontsize=14)
        ax.set_xlabel("Transaction Count")
        ax.set_ylabel("Category")
        st.pyplot(fig)

        # **12. Get Total Spend on Utilities
        st.subheader("📈 Total Spend in Utilities")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.lineplot(x="DATE", y="AMOUNTS", data=df, marker="o", color="blue")
        ax.set_title("Utilities Expenses", fontsize=14)
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount Spent ($)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # **14. Percentage depiction of Online transactions vs Cash transactions
        st.subheader("💳 Online vs. Cash Transactions")
        total_transactions = len(df)
        online_transactions = df[df["PAYMENT_MODE"].isin(['Paytm', 'Gpay', 'Credit_card', 'Debit_card', 'Paypal', 'Bank_transfer', 'Visa'])].shape[0]
        cash_transactions = df[df["PAYMENT_MODE"].isin(['Cash', 'Check'])].shape[0]
        online_percentage = (online_transactions / total_transactions) * 100
        cash_percentage = (cash_transactions / total_transactions) * 100
        st.write(f"**Online Transactions:** {online_percentage:.2f}%")
        st.write(f"**Cash Transactions:** {cash_percentage:.2f}%")
        labels = ["Online Transactions", "Cash Transactions"]
        sizes = [online_percentage, cash_percentage]
        colors = ["skyblue", "pink"]
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
        ax.set_title("Online vs. Cash Transactions")
        st.pyplot(fig)

        # **15. Total spend per month 
        st.subheader("📊 Total Amount Spent Per Month")
        if df.empty:
          st.warning("No expense data available. Please add some records.")
        else:
         df['MONTH'] = pd.to_datetime(df['MONTH'], format='%Y-%m')
         Data = df
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=df, x="MONTH", y="AMOUNTS", palette="viridis", ax=ax)
        ax.set_xlabel("MONTH", fontsize=12)
        ax.set_ylabel("Total Amount Spent", fontsize=12)
        ax.set_title("Total Amount Spent Per Month", fontsize=14)
        plt.xticks(rotation=45)  # Rotate labels for better readability
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)


# Close Database Connection
conn.close()



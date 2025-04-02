import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from faker import Faker
from datetime import date, timedelta

# Initialize Faker
fake = Faker()

# Define Categories and Payment Modes
Categories = ['Groceries', 'Utilities', 'Rent', 'Entertainment', 'Insurance', 'Travel', 'Subscription']
Payment_mode = ['Paytm', 'Gpay', 'Credit_card', 'Debit_card', 'Cash', 'Paypal', 'Check', 'Bank_transfer', 'Visa']

# SQLite Database Setup
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

# Create Table
cursor.execute('''CREATE TABLE IF NOT EXISTS Expense_Table (
                    DATE TEXT,
                    CATEGORIES TEXT, 
                    PAYMENT_MODE TEXT, 
                    DESCRIPTION TEXT, 
                    AMOUNTS REAL, 
                    CASHBACK REAL)''')
conn.commit()

# Load or create expense data
@st.cache_data
def load_data():
    try:
        return pd.read_sql("SELECT * FROM Expense_Table", conn)
    except:
        return pd.DataFrame(columns=["DATE", "CATEGORIES", "PAYMENT_MODE", "DESCRIPTION", "AMOUNTS", "CASHBACK"])

df = load_data()

# Sidebar Navigation
st.sidebar.title("Expense Tracker")
page = st.sidebar.radio("Go to", ["Home", "Expense Tracker", "Analyze Expenses"])

if page == "Home":
    st.title("Welcome to the Expense Tracker App")
    st.write("""
        This application helps you track and analyze your personal expenses.
        Navigate through the sections to explore visualizations and insights.
    """)

elif page == "Expense Tracker":
    st.header("Expense Tracker")

    query_dict = {
         "Total amount spent using each payment mode" :
      'SELECT Payment_mode, '
      'SUM(amounts) AS Total_Spend '
      'FROM Expense_Table GROUP BY Payment_mode',

     "Total amount spent in each category":
      'SELECT categories, '
      'SUM(amounts) AS expense_by_category '
      'FROM Expense_Table GROUP BY categories',

      "Total cashback received across all transactions" :
      'SELECT SUM(Cashback) AS Total_Cashback'
      'FROM Expense_Table',
       
       "Top 5 most expensive categories in terms of spending":
       'SELECT Categories,'
       'SUM(Amounts) AS total_spend'
       'SELECT Categories, '
       'SUM(Amounts) AS total_spent '
       'FROM Expense_Table GROUP BY Categories limit 5',

       "Spent on transportation using different payment modes":
       'SELECT Payment_Mode, SUM(Amounts) AS Total_Spent '
       'FROM Expense_Table '
       'WHERE Categories = "Travel" '
       'GROUP BY Payment_Mode',

       "Transactions resulted in cashback" :
       'SELECT * FROM Expense_Table '
       'WHERE Cashback > 0',

       "The total spending in each month of the year":
       '''SELECT strftime('%Y-%m', Amounts) AS Month, SUM(Amounts) AS Total_Spent
        FROM Expense_Table
        GROUP BY Month
        ORDER BY Month''',

        "Which months have the highest spending in categories like Travel,Entertainment,Gifts?" :
        '''
        SELECT strftime('%Y-%m', Amounts) AS Month, 
        Categories, 
        SUM(Amounts) AS Total_Spent
        FROM Expense_Table
        WHERE Categories IN ('Travel', 'Entertainment', 'Gifts')
        GROUP BY strftime('%Y-%m', Date), Categories
        ORDER BY Total_Spent DESC
        ''',

        "Are there any recurring expenses that occur during specific months of the year (e.g., insurance premiums, property taxes)?":
        '''
        SELECT strftime('%Y-%m', Date) AS Month, 
        Categories, 
        COUNT(*) AS Occurrences, 
        SUM(Amounts) AS Total_Spent
        FROM Expense_Table
        WHERE Categories IN ('Insurance', 'Property Taxes')  -- Adjust for relevant categories
        GROUP BY strftime('%Y-%m', Date), Categories
        HAVING COUNT(*) > 1  -- Only show recurring expenses that occur multiple times in the same month
        ORDER BY Month''',

        "Cashback or rewards were earned in each month" :
        '''
        SELECT strftime('%Y-%m', Date) AS Month, 
        SUM(Cashback) AS Total_Cashback
        FROM Expense_Table
        WHERE Cashback > 0  -- Only include transactions where cashback is greater than 0
        GROUP BY strftime('%Y-%m', Date)
        ORDER BY Month
        ''',

        "Overall spending changed over time (e.g., increasing, decreasing, remaining stable)":
        '''
        SELECT strftime('%Y-%m', date) AS month, SUM(Amounts) AS total_spending
        FROM Expense_Table
        GROUP BY month
        ORDER BY month;
        ''',

        "Total spend in Subscription":
        """
        SELECT SUM(AMOUNTS) 
        FROM Expense_Table 
        WHERE CATEGORIES = 'Subscription';
        """,

        "Which categories have the most number of transactions?" :
         '''
        SELECT Categories, COUNT(*) AS Amounts
        FROM Expense_Table
        GROUP BY Categories
        ORDER BY Amounts DESC;
        ''',

        "Sum of the expenses by category and find the one with the highest total expense":
        '''
        SELECT CATEGORIES, SUM(AMOUNTS) AS Total_Expense
        FROM Expense_Table
        GROUP BY CATEGORIES
        ORDER BY Total_Expense DESC
        LIMIT 1;
        ''',

        "How much spend in Ultilites ?":
        
        '''SELECT * FROM Expense_Table WHERE CATEGORIES = "Utilities"
        ''',

        "The day with the lowest expenditure":
        """
        SELECT DATE, 
           strftime('%w', DATE) AS Weekday, 
           SUM(AMOUNTS) AS Total_Spent
        FROM Expense_Table
        GROUP BY DATE
        ORDER BY Total_Spent ASC
        LIMIT 1
        """,

        "Number of transactions made per day":
        """
        SELECT DATE, COUNT(*) AS Transaction_Count
        FROM Expense_Table
        GROUP BY DATE
        ORDER BY DATE ASC
        """,

        "Number of transactions made each month":

        """
        SELECT strftime('%Y-%m', DATE) AS Month, COUNT(*) AS Transaction_Count
        FROM Expense_Table
        GROUP BY Month
        ORDER BY Month ASC
        """,

        "The day with the highest expenditure":
        """
        SELECT DATE, SUM(AMOUNTS) AS Total_Spent
        FROM Expense_Table
        GROUP BY DATE
        ORDER BY Total_Spent DESC
        LIMIT 1
        """,

        "Total amount spent per month":
        """
        SELECT 
            CASE 
                WHEN strftime('%m', date) = '01' THEN 'January'
                WHEN strftime('%m', date) = '02' THEN 'February'
                WHEN strftime('%m', date) = '03' THEN 'March'
                WHEN strftime('%m', date) = '04' THEN 'April'
                WHEN strftime('%m', date) = '05' THEN 'May'
                WHEN strftime('%m', date) = '06' THEN 'June'
                WHEN strftime('%m', date) = '07' THEN 'July'
                WHEN strftime('%m', date) = '08' THEN 'August'
                WHEN strftime('%m', date) = '09' THEN 'September'
                WHEN strftime('%m', date) = '10' THEN 'October'
                WHEN strftime('%m', date) = '11' THEN 'November'
                WHEN strftime('%m', date) = '12' THEN 'December'
            END AS month_name,
            SUM(AMOUNTS) AS Total_spent
        FROM Expense_Table
        GROUP BY month_name
        ORDER BY strftime('%m', date)
        """,
}
    

    st.title("Expense Tracker - Query Results")

    # Dropdown to select a query
    selected_query = st.selectbox("Select a query to execute:", list(query_dict.keys()))

    # Run the selected query and display results
    if selected_query:
        query = query_dict[selected_query]
        df_result = pd.read_sql(query, conn)
        st.write(df_result)


# Analyze Expenses Page
elif page == "Analyze Expenses":
    st.title("📊 Expense Analysis")
    df = load_data()
    
    if df.empty:
        st.warning("No expense data available for analysis.")
    else:
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["MONTH"] = df["DATE"].dt.strftime("%Y-%m")
          
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



import streamlit as st
import pandas as pd
import sqlite3

# Define CSV file paths
customers_csv_path = 'customers.csv'
orders_csv_path = 'orders.csv'

# Load data from CSV files
customers_df = pd.read_csv(customers_csv_path)
orders_df = pd.read_csv(orders_csv_path)

# Initialize the in-memory SQLite database
conn = sqlite3.connect(':memory:')
customers_df.to_sql('customers', conn, if_exists='replace', index=False)
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], format='%d.%m.%Y %H:%M:%S')
orders_df.to_sql('orders', conn, if_exists='replace', index=False)

# Dictionary to store usernames and passwords
users = {
    "test": "test2024!",
    # Add more users as needed
}

# User authentication
def authenticate(username, password):
    if username in users and password == users[username]:
        return True
    return False

# Set wide layout for Streamlit app
st.set_page_config(layout="wide")

# Streamlit UI
st.title('SQL Test')

# Initialize session state
if 'query1_result' not in st.session_state:
    st.session_state.query1_result = None
if 'query2_result' not in st.session_state:
    st.session_state.query2_result = None
if 'query3_result' not in st.session_state:
    st.session_state.query3_result = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Questions and correct answers
questions = [
    "What is the total number of customers?",
    "What is the total number of orders?",
    "What is the average order amount? Round to nearest integer.",
    "Which customer has placed the highest number of orders?",
    "What is the most recent order date?"
]
correct_answers = [
    str(customers_df.shape[0]),
    str(orders_df.shape[0]),
    str(int(orders_df['total_amount'].mean().round())),  # Average order amount as integer
    customers_df.loc[orders_df.groupby('customer_id').size().idxmax(), 'customer_name'],
    str(orders_df['order_date'].max())
]

# Initialize session state for questions
for i in range(len(questions)):
    if f"submitted_{i+1}" not in st.session_state:
        st.session_state[f"submitted_{i+1}"] = False
    if f"answer_{i+1}" not in st.session_state:
        st.session_state[f"answer_{i+1}"] = ""
    if f"evaluation_{i+1}" not in st.session_state:
        st.session_state[f"evaluation_{i+1}"] = ""

# Login form
if not st.session_state.logged_in:
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success('Logged in successfully')
        else:
            st.error('Invalid username or password')
else:
    st.write('You are a data analyst at an e-commerce company. Your manager has asked you to analyze the orders placed by customers and respond to several questions (find them at the end).')
    st.write('The data is stored in the tables named **customers** and **orders**. Total_amount refers to Revenue in USD. Below you can find in-built querying options (SQL-Lite).')

    # Create columns layout with custom widths
    col1, col2, col3 = st.columns([1.8, 2, 2.3])

    # Input and result for SQL query 1 (smallest)
    with col1:
        st.subheader('Query 1')
        query1 = st.text_area('Enter your SQL query here:', 'SELECT * FROM customers')
        if st.button('Run Query 1'):
            try:
                query1_result = pd.read_sql_query(query1, conn)
                st.session_state.query1_result = query1_result
            except Exception as e:
                st.error(f'Error: {e}')

        # Display result of Query 1
        if st.session_state.query1_result is not None:
            st.dataframe(st.session_state.query1_result)

    # Input and result for SQL query 2 (bigger)
    with col2:
        st.subheader('Query 2')
        query2 = st.text_area('Enter your SQL query here:', 'SELECT * FROM orders')
        if st.button('Run Query 2'):
            try:
                query2_result = pd.read_sql_query(query2, conn)
                st.session_state.query2_result = query2_result
            except Exception as e:
                st.error(f'Error: {e}')

        # Display result of Query 2
        if st.session_state.query2_result is not None:
            st.dataframe(st.session_state.query2_result)

    # Input and result for SQL query 3 (biggest)
    with col3:
        st.subheader('Query 3')
        query3 = st.text_area('Enter your SQL query here:', 'SELECT min(order_date) FROM orders')
        if st.button('Run Query 3'):
            try:
                query3_result = pd.read_sql_query(query3, conn)
                st.session_state.query3_result = query3_result
            except Exception as e:
                st.error(f'Error: {e}')

        # Display result of Query 3
        if st.session_state.query3_result is not None:
            st.dataframe(st.session_state.query3_result)

    # Questions and answers section
    st.subheader('Questions')
    for i, question in enumerate(questions):
        with st.container():
            cols = st.columns([1, 1, 5])
            cols[0].write(f"**Question {i+1}:** {question}")
            answer = cols[1].text_input(f"Your answer for question {i+1}", key=f"input_{i+1}", disabled=st.session_state[f"submitted_{i+1}"])
            if not st.session_state[f"submitted_{i+1}"]:
                if cols[2].button(f"Submit answer {i+1}", key=f"submit_{i+1}"):
                    st.session_state[f"submitted_{i+1}"] = True
                    st.session_state[f"answer_{i+1}"] = answer
                    if answer == correct_answers[i]:
                        st.session_state[f"evaluation_{i+1}"] = f"Correct. The correct answer is {correct_answers[i]}."
                    else:
                        st.session_state[f"evaluation_{i+1}"] = f"answer_{i+1} is incorrect. The correct answer is {correct_answers[i]}."
            else:
                cols[2].write(st.session_state[f"evaluation_{i+1}"])

    # Logout button
    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success('Logged out successfully')

# Close the connection when done
conn.close()

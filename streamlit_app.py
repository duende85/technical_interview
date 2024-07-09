import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

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
    "user": "user2024!",
    # Add more users as needed
}

# User authentication
def authenticate(username, password):
    if username in users and password == users[username]:
        return True
    return False

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
    str(orders_df['customer_id'].value_counts().idxmax()),
    str(orders_df['order_date'].max())
]

# Initialize session state for questions
if 'question_results' not in st.session_state:
    st.session_state.question_results = [None] * len(questions)  # Initialize with None
if 'answers' not in st.session_state:
    st.session_state.answers = [""] * len(questions)  # Initialize with empty strings

# Set wide layout for Streamlit app
st.set_page_config(layout="wide")

# Streamlit UI
st.title('SQL Test')

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'login_time' not in st.session_state:
    st.session_state.login_time = None
if 'self_assessment' not in st.session_state:
    st.session_state.self_assessment = None  # Initialize as None
if 'query1_result' not in st.session_state:
    st.session_state.query1_result = None
if 'query2_result' not in st.session_state:
    st.session_state.query2_result = None
if 'query3_result' not in st.session_state:
    st.session_state.query3_result = None

# Login form
if not st.session_state.logged_in:
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    # Prompt for self-assessment rating using radio buttons
    st.write('Rate your SQL knowledge from 0 to 10:')
    self_assessment = st.radio('', options=list(range(11)), index=0)

    if st.button('Login', disabled=self_assessment is None):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_time = datetime.now()
            st.session_state.self_assessment = self_assessment  # Ensure self_assessment is an integer
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
            st.session_state.answers[i] = cols[1].text_input(f"Your answer for question {i+1}", key=f"input_{i+1}")

    if st.button("Submit All Answers"):
        for i, correct_answer in enumerate(correct_answers):
            answer = st.session_state.answers[i]
            st.session_state.question_results[i] = 1 if answer == correct_answer else 0
            if answer == correct_answer:
                st.session_state[f"evaluation_{i+1}"] = f"Correct.   Your answer: {answer}. The correct answer is {correct_answer}."
            else:
                st.session_state[f"evaluation_{i+1}"] = f"Incorrect. Your answer: {answer}. The correct answer is {correct_answer}."
        
        for i, question in enumerate(questions):
            st.write(f"**Question {i+1}:** {question}")
            st.write(st.session_state[f"evaluation_{i+1}"])

    # Logout button
    if st.button('Logout'):
        logout_time = datetime.now()
        log_entry = f"{st.session_state.username},{st.session_state.login_time},{logout_time},{st.session_state.self_assessment},"
        log_entry += ','.join(map(str, st.session_state.question_results))
        log_entry += f",{sum(filter(None, st.session_state.question_results))}"  # sum only non-None results

        # Write log entry to file
        log_file_path = 'logs.txt'
        with open(log_file_path, 'a') as f:
            f.write(log_entry + "\n")

        st.session_state.logged_in = False
        st.session_state.username = None
        st.success('Logged out successfully')

# Close the connection when done
conn.close()

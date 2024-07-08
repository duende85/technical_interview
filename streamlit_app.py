import streamlit as st
import pandas as pd
import sqlite3
import subprocess

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

# Function to save the DataFrame back to CSV and commit to GitHub
def save_to_csv_and_commit(df, csv_path):
    df.to_csv(csv_path, index=False)
    try:
        subprocess.run(['git', 'add', csv_path], check=True)
        subprocess.run(['git', 'commit', '-m', f'Update {csv_path}'], check=True)
        subprocess.run(['git', 'push'], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f'Error during Git operations: {e}')

# Dictionary to store usernames and passwords
users = {
    "test": "testtest1294!",
    # Add more users as needed
}

# User authentication
def authenticate(username, password):
    # Check if the username exists in the dictionary
    if username in users:
        # Retrieve the stored password for the username
        stored_password = users[username]
        # Check if the provided password matches the stored password
        if password == stored_password:
            return True  # Authentication successful
    return False  # Authentication failed

# Streamlit UI
st.title('SQL Test')

# Login form
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
    st.write(f'Welcome, {st.session_state.username}!')
    st.write('You are a data analyst at an e-commerce company. Your manager has asked you to analyze the orders placed by customers in the North America region. You need to identify the most recent order for each customer in North America and provide details about the customer and their order.')
    st.write('The data is stored in the tables named **customers** and **orders**.')
    
    # Create two columns for query inputs and results
    col1, col2 = st.columns(2)
    
    # List to store query results
    query_results = {
        'query1': None,
        'query2': None
    }
    
    # Input and result for SQL query 1 (first column)
    with col1:
        st.subheader('Query 1')
        query1 = st.text_area('Enter your SQL query here:', 'SELECT * FROM customers')
        if st.button('Run Query 1'):
            try:
                query_results['query1'] = pd.read_sql_query(query1, conn)
            except Exception as e:
                st.error(f'Error: {e}')
        
        # Display result of Query 1
        if query_results['query1'] is not None:
            st.dataframe(query_results['query1'])

    # Input and result for SQL query 2 (second column)
    with col2:
        st.subheader('Query 2')
        query2 = st.text_area('Enter your SQL query here:', 'SELECT * FROM orders')
        if st.button('Run Query 2'):
            try:
                query_results['query2'] = pd.read_sql_query(query2, conn)
            except Exception as e:
                st.error(f'Error: {e}')
        
        # Display result of Query 2
        if query_results['query2'] is not None:
            st.dataframe(query_results['query2'])

    # Logout button
    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success('Logged out successfully')

# Close the connection when done
conn.close()

import streamlit as st
import pandas as pd
import psycopg2
import requests
from io import StringIO

# Define URLs for CSV files
customers_csv_url = 'https://raw.githubusercontent.com/duende85/technical_interview/main/customers.csv'
orders_csv_url = 'https://raw.githubusercontent.com/duende85/technical_interview/main/orders.csv'

# Load data from GitHub URLs
@st.cache_data
def load_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return pd.read_csv(StringIO(response.text))

customers_df = load_data(customers_csv_url)
orders_df = load_data(orders_csv_url)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='mysecretpassword',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# Create tables and load data
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    country VARCHAR(50)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT,
    order_date TIMESTAMP,
    total_amount DECIMAL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);
""")

# Insert data into PostgreSQL tables
# Clear existing data first for demonstration purposes
cursor.execute("DELETE FROM customers; DELETE FROM orders;")

cursor.executemany("""
INSERT INTO customers (first_name, last_name, email, phone, country)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
""", customers_df[['first_name', 'last_name', 'email', 'phone', 'country']].values.tolist())

orders_df['order_date'] = pd.to_datetime(orders_df['order_date'], format='%d.%m.%Y %H:%M:%S')
cursor.executemany("""
INSERT INTO orders (customer_id, order_date, total_amount)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING;
""", orders_df[['customer_id', 'order_date', 'total_amount']].values.tolist())

conn.commit()

# Dictionary to store usernames and passwords
users = {
    "test": "testtest",
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
    st.write('You are a data analyst at an e-commerce company. Your manager has asked you to analyze the orders placed by customers in the North America region.')
    st.write('You need to identify the most recent order for each customer in North America and provide details about the customer and their order.')
    st.write('The data is stored in the tables named **customers** and **orders**.')

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
        query3 = st.text_area('Enter your SQL query here:', '')
        if st.button('Run Query 3'):
            try:
                query3_result = pd.read_sql_query(query3, conn)
                st.session_state.query3_result = query3_result
            except Exception as e:
                st.error(f'Error: {e}')

        # Display result of Query 3
        if st.session_state.query3_result is not None:
            st.dataframe(st.session_state.query3_result)

    # Logout button
    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success('Logged out successfully')

# Close the connection when done
cursor.close()
conn.close()

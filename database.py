import psycopg2
import streamlit as st
import os

def get_db_connection():  # Renamed to match what Home.py expects
    try:
        # Get credentials from Render Environment Variables
        host = os.environ.get('DB_HOST')
        port = os.environ.get('DB_PORT')
        database = os.environ.get('DB_NAME')
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASS')

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        st.error(f"Could not connect to the cloud database: {e}")
        return None

def execute_query(query, params=None):
    conn = get_db_connection() # This now matches the function name above
    if conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()

def fetch_query(query, params=None):
    conn = get_db_connection() # This now matches the function name above
    if conn:
        cur = conn.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    return []

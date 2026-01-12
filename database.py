import psycopg2
import streamlit as st
import os

# This checks Render variables first, then falls back to st.secrets for local testing
DB_HOST = os.environ.get('DB_HOST') or st.secrets["postgres"]["host"]
DB_USER = os.environ.get('DB_USER') or st.secrets["postgres"]["user"]
# ... do the same for password, port, and database name

# this connects us to the supabase cloud
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"Could not connect to the cloud database: {e}")
        return None

# for saving data (insert/update/delete)
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()

# for getting data back to display it
def fetch_query(query, params=None):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute(query, params)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    return []

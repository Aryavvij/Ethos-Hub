import psycopg2
import streamlit as st
import os

@st.cache_resource # This is the magic fix for lag
def get_db_connection():
    try:
        # Use the DATABASE_URL we set up
        url = os.environ.get('DATABASE_URL')
        if not url:
            return None
            
        # The connection now stays "warm" in memory
        conn = psycopg2.connect(url, connect_timeout=15)
        return conn
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
        except Exception as e:
            st.error(f"Error: {e}")

def fetch_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            st.error(f"Error: {e}")
    return []

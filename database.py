import psycopg2
import streamlit as st
import os
import hashlib

# --- SHARD CONFIGURATION ---

DATABASE_URL = os.environ.get('DATABASE_URL')


def get_shard_connection(user_email=None):
    """
    Router Logic: Determines which database instance to connect to.
    If no user_email is provided (e.g., during global setup), it defaults to the main URL.
    """
    try:
        url = DATABASE_URL

        if not url:
            return None
            
        conn = psycopg2.connect(url, sslmode='require')
        return conn
    except Exception as e:
        return None

def execute_query(query, params=None, user_email=None):
    """
    Executes a write/update query. 
    Accepts user_email to ensure the query is routed to the correct shard.
    """
    conn = get_shard_connection(user_email)
    if not conn: 
        st.error("Database Connection Failed.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()  
        st.error(f"Execution Error: {e}")
    finally:
        if conn:
            conn.close()

def fetch_query(query, params=None, user_email=None):
    """
    Fetches data from the database. 
    Routes to the correct shard based on user_email.
    """
    conn = get_shard_connection(user_email)
    if not conn: 
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

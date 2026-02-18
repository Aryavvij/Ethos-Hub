import psycopg2
from psycopg2 import pool
import streamlit as st
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

@st.cache_resource
def get_connection_pool():
    """Create a single pool that lasts the entire app lifecycle."""
    try:
        # Use a smaller pool (min 1, max 5) to avoid hitting DB limits
        return psycopg2.pool.SimpleConnectionPool(
            1, 5, DATABASE_URL, sslmode='require'
        )
    except Exception as e:
        st.error(f"Critical Database Connection Error: {e}")
        return None

def execute_query(query, params=None):
    db_pool = get_connection_pool()
    if not db_pool: return
    
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit() 
    except Exception as e:
        print(f"Execute Error: {e}")
    finally:
        if conn:
            db_pool.putconn(conn)

def fetch_query(query, params=None):
    db_pool = get_connection_pool()
    if not db_pool: return []
    
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []
    finally:
        if conn:
            db_pool.putconn(conn)

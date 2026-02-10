import psycopg2
import streamlit as st
import os
from psycopg2 import pool

# --- CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_pool(db_url):
    """
    Creates or retrieves a connection pool safely using Lazy Initialization.
    This prevents the AttributeError by ensuring the session_state key exists
    at the moment it's requested.
    """
    if 'db_pools' not in st.session_state:
        st.session_state.db_pools = {}

    if db_url not in st.session_state.db_pools:
        try:
            st.session_state.db_pools[db_url] = psycopg2.pool.SimpleConnectionPool(
                1, 10, db_url, sslmode='require'
            )
        except Exception as e:
            st.error(f"Failed to initialize Connection Pool: {e}")
            return None
    return st.session_state.db_pools[db_url]



def get_shard_url(user_email=None):
    """Router: Maps a user to a specific database URL."""
    return DATABASE_URL

def execute_query(query, params=None, user_email=None):
    """Executes a write query using Connection Pooling."""
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    if not db_pool: 
        return
    
    conn = db_pool.getconn() 
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"Database Execution Error: {e}")
    finally:
        if db_pool and conn:
            db_pool.putconn(conn) 

def fetch_query(query, params=None, user_email=None):
    """Fetches data using Connection Pooling."""
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    if not db_pool: 
        return []
    
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        st.error(f"Database Fetch Error: {e}")
        return []
    finally:
        if db_pool and conn:
            db_pool.putconn(conn)

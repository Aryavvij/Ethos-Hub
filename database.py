import psycopg2
import streamlit as st
import os

def get_db_connection():
    try:
        url = os.environ.get('DATABASE_URL')
        if not url:
            return None
        # Fresh connection every time to prevent timeouts
        conn = psycopg2.connect(url, sslmode='require')
        return conn
    except Exception as e:
        return None

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
    except Exception as e:
        conn.rollback() # Fixes "Aborted Transaction"
        st.error(f"Database Error: {e}")
    finally:
        conn.close() # Fixes "Server closed connection"

def fetch_query(query, params=None):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

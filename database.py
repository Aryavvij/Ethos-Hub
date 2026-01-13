import streamlit as st
import os

# 1. REMOVE @st.cache_resource. It keeps "dead" connections alive.
def get_db_connection():
try:
url = os.environ.get('DATABASE_URL')
if not url:
return None
        # Use a fresh connection every time
        # Fresh connection every time to prevent timeouts
conn = psycopg2.connect(url, sslmode='require')
return conn
except Exception as e:
return None

def execute_query(query, params=None):
conn = get_db_connection()
    if not conn:
        return
    if not conn: return
try:
        # Using a 'with' block ensures the cursor closes automatically
with conn.cursor() as cur:
cur.execute(query, params)
conn.commit()
except Exception as e:
        conn.rollback()  # CRITICAL: This clears the "Aborted Transaction" error
        conn.rollback() # Fixes "Aborted Transaction"
st.error(f"Database Error: {e}")
finally:
        conn.close()  # CRITICAL: This prevents "Server closed connection" errors
        conn.close() # Fixes "Server closed connection"

def fetch_query(query, params=None):
conn = get_db_connection()
    if not conn:
        return []
    if not conn: return []
try:
with conn.cursor() as cur:
cur.execute(query, params)
return cur.fetchall()
    except Exception as e:
        # No rollback needed for fetch, but we catch errors
        return []
finally:
        conn.close() # Always close the door when finished
        conn.close()

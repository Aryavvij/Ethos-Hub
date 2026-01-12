import psycopg2
import streamlit as st
import os

# Function to get a connection to the Supabase cloud database
def get_db_connection():
    try:
        # 1. Try to get credentials from Render Environment Variables first
        # 2. Fall back to st.secrets for local testing (Streamlit)
        host = os.environ.get('DB_HOST') or st.secrets["postgres"]["host"]
        port = os.environ.get('DB_PORT') or st.secrets["postgres"]["port"]
        database = os.environ.get('DB_NAME') or st.secrets["postgres"]["database"]
        user = os.environ.get('DB_USER') or st.secrets["postgres"]["user"]
        password = os.environ.get('DB_PASS') or st.secrets["postgres"]["password"]

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"Could not connect to the cloud database: {e}")
        return None

# Standard function for saving data (insert/update/delete)
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
        except Exception as e:
            st.error(f"Error executing query: {e}")
        finally:
            conn.close()

# Standard function for retrieving data to display
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
            st.error(f"Error fetching data: {e}")
            return []
        finally:
            conn.close()
    return []

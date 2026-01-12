import psycopg2
import streamlit as st
import os

def get_db_connection():
    try:
        host = os.environ.get('DB_HOST')
        port = os.environ.get('DB_PORT')
        database = os.environ.get('DB_NAME')
        # HARD-CODED USERNAME TO BYPASS RENDER DASHBOARD ERRORS
        user = "postgres.lyquddfadowlaosrnwhdb" 
        password = os.environ.get('DB_PASS')

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
        # This will show exactly what the code is trying to use
        st.error(f"Failed with User: {user}")
        st.error(f"Error: {e}")
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

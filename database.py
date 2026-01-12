import psycopg2
import streamlit as st
import os

def get_db_connection():
    try:
        host = "db.lyquddfadowlaosrwnwb.supabase.co" 
        port = 5432  
        database = "postgres"
        user = "postgres" 
        password = os.environ.get('DB_PASS') or "Aryav_vij04"

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=15
        )
        return conn
    except Exception as e:
        st.error(f"Direct Connection Attempt Failed")
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

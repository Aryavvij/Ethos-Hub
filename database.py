import psycopg2
import streamlit as st
import os

def get_db_connection():
    try:
        # Use the URI with sslmode=require added to the end
        conn_str = os.environ.get('DATABASE_URL') or "postgresql://postgres.lyquddfadowlaosrwnwb:Aryav_vij04@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
        
        # Adding sslmode for better cloud compatibility
        conn = psycopg2.connect(conn_str, sslmode='require', connect_timeout=15)
        return conn
    except Exception as e:
        st.error(f"Connection Failed - Tenant: lyquddfadowlaosrwnwb")
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

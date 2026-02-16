import psycopg2
import streamlit as st
import os
from psycopg2 import pool
from services.observability import Telemetry

# --- CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_pool(db_url):
    if not db_url: 
        return None
    if 'db_pools' not in st.session_state:
        st.session_state.db_pools = {}
    if db_url not in st.session_state.db_pools:
        try:
            st.session_state.db_pools[db_url] = psycopg2.pool.SimpleConnectionPool(
                1, 20, db_url, sslmode='require'
            )
        except Exception as e:
            st.error(f"Failed to initialize Connection Pool: {e}")
            return None
    return st.session_state.db_pools[db_url]

def get_shard_url(user_email=None):
    return DATABASE_URL

def execute_query(query, params=None, user_email=None):
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    if not db_pool: 
        return
    
    with Telemetry.track_latency(f"DB_Execute: {query[:30]}..."):
        conn = None
        try:
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit() 
        except Exception as e:
            Telemetry.log('ERROR', 'Database_Execute_Failure', metadata={'error': str(e), 'query': query})
            st.error("ETHOS: Command failed to sync.")
        finally:
            if conn:
                db_pool.putconn(conn)

def fetch_query(query, params=None, user_email=None):
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    if not db_pool: 
        return []
    
    with Telemetry.track_latency(f"DB_Fetch: {query[:30]}..."):
        conn = None
        try:
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            Telemetry.log('ERROR', 'Database_Fetch_Failure', metadata={'error': str(e), 'query': query})
            st.error("ETHOS: System link unstable.")
            return []
        finally:
            if conn:
                db_pool.putconn(conn)

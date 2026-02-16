import psycopg2
import streamlit as st
import os
from psycopg2 import pool
from services.observability import Telemetry

# --- CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL')

@st.cache_data(ttl=600) 
def fetch_timetable_cached(email):
    return fetch_query("SELECT * FROM timetable WHERE user_email=%s", (email,))

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
    """Executes data mutations using Connection Pooling with integrated Observability."""
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    
    if not db_pool: 
        Telemetry.log('ERROR', 'DB_Pool_Unavailable_Execute', metadata={'user': user_email})
        return
    
    with Telemetry.track_latency(f"DB_Execute: {query[:30]}..."):
        conn = None
        try:
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit() 
        except Exception as e:
            Telemetry.log('ERROR', 'Database_Execute_Failure', metadata={
                'error': str(e),
                'query': query,
                'user': user_email
            })
            
            st.error("ETHOS: Command failed to synchronize. Data integrity preserved.")
        finally:
            if conn:
                db_pool.putconn(conn)

def fetch_query(query, params=None, user_email=None):
    """Fetches data using Connection Pooling with integrated Observability."""
    url = get_shard_url(user_email)
    db_pool = get_pool(url)
    
    if not db_pool: 
        Telemetry.log('ERROR', 'DB_Pool_Unavailable', metadata={'user': user_email})
        return []
    
    with Telemetry.track_latency(f"DB_Fetch: {query[:30]}..."):
        conn = None
        try:
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            Telemetry.log('ERROR', 'Database_Fetch_Failure', metadata={
                'error': str(e),
                'query': query,
                'user': user_email
            })
            
            st.error("ETHOS: System link unstable")
            return []
        finally:
            if conn:
                db_pool.putconn(conn)
            

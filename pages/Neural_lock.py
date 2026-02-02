import streamlit as st
import time
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Neural Lock", page_icon="🔒")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
now = datetime.now()
t_date = now.date()
st.title("🔒 Neural Lock")
st.caption(f"Protocol Active for {t_date.strftime('%A, %b %d, %Y')}")

st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- PERSISTENT STOPWATCH ENGINE ---
st.markdown("---")
col_timer, col_log = st.columns([1.2, 1], gap="large")


active_session = fetch_query("SELECT task_name, start_time FROM active_sessions WHERE user_email=%s", (user,))

with col_timer:
    st.subheader("Focus Session")
    timer_placeholder = st.empty()
    action_placeholder = st.empty()

    if not active_session:
        task_input = st.text_input("Objective", placeholder="What are you crushing right now?", key="new_task_input", label_visibility="collapsed")
        
        timer_placeholder.markdown("""
            <div style="text-align: center; border: 2px solid #333; padding: 40px; border-radius: 15px; background: rgba(255, 255, 255, 0.02);">
                <h1 style="font-size: 60px; color: #444; margin: 0; font-family: monospace;">00:00</h1>
                <p style="color: #666; letter-spacing: 2px;">READY TO INITIATE</p>
            </div>
        """, unsafe_allow_html=True)

        if action_placeholder.button("INITIATE STOPWATCH", use_container_width=True, type="primary"):
            if task_input:
                execute_query("INSERT INTO active_sessions (user_email, task_name, start_time) VALUES (%s, %s, %s)", 
                              (user, task_input, datetime.now()))
                st.rerun()
            else:
                st.error("Define an objective first.")
    else:
        task_name, start_time = active_session[0]
        
        elapsed_delta = datetime.now() - start_time
        elapsed_seconds = int(elapsed_delta.total_seconds())
        mins, secs = divmod(elapsed_seconds, 60)
        hours, mins = divmod(mins, 60)

        timer_placeholder.markdown(f"""
            <div style="text-align: center; border: 2px solid #76b372; padding: 40px; border-radius: 15px; background: rgba(118, 179, 114, 0.05);">
                <h1 style="font-size: 60px; color: #76b372; margin: 0; font-family: monospace;">{hours:02d}:{mins:02d}:{secs:02d}</h1>
                <p style="color: #76b372; letter-spacing: 5px; font-weight: bold;">LOCKED ON: {task_name.upper()}</p>
            </div>
        """, unsafe_allow_html=True)

        if action_placeholder.button("🛑 STOP & LOG SESSION", use_container_width=True):
            duration_mins = max(1, elapsed_seconds // 60)
            
            execute_query("INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, CURRENT_DATE)",
                          (user, task_name, duration_mins))
            
            execute_query("DELETE FROM active_sessions WHERE user_email=%s", (user,))
            st.rerun()
        time.sleep(1)
        st.rerun()

# --- SESSION LOG & DELETION ---
with col_log:
    st.subheader("Today's Log")
    today_data = fetch_query("SELECT id, task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = CURRENT_DATE ORDER BY id DESC", (user,))
    
    if today_data:
        log_df = pd.DataFrame(today_data, columns=["ID", "Objective", "Duration"])
        st.dataframe(log_df.drop(columns=["ID"]), use_container_width=True, hide_index=True,
                     column_config={"Duration": st.column_config.NumberColumn("Mins", format="%d m")})
        
        with st.expander("Delete Session"):
            session_options = {f"{row[1]} ({row[2]}m)": row[0] for row in today_data}
            to_delete = st.selectbox("Select session to remove", options=list(session_options.keys()))
            if st.button("Confirm Delete", use_container_width=True):
                execute_query("DELETE FROM focus_sessions WHERE id=%s", (session_options[to_delete],))
                st.rerun()

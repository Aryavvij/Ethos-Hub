import streamlit as st
import time
import pandas as pd
from database import execute_query, fetch_query
from datetime import datetime, timedelta

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Neural Lock")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("🔒 Neural Lock")
st.caption("Active Session Stopwatch & Cognitive Tracker")

# --- 3. MOMENTUM METRICS ---
today_date = datetime.now().date()
start_of_week = today_date - timedelta(days=today_date.weekday())

today_data = fetch_query("SELECT SUM(duration_mins) FROM focus_sessions WHERE user_email=%s AND session_date=%s", (user, today_date))
today_total = today_data[0][0] if today_data[0][0] else 0

weekly_data = fetch_query("SELECT SUM(duration_mins) FROM focus_sessions WHERE user_email=%s AND session_date >= %s", (user, start_of_week))
weekly_total = weekly_data[0][0] if weekly_data[0][0] else 0

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Daily Neural Output", f"{today_total} Mins")
    st.progress(min(today_total / 120, 1.0))
with m2:
    st.metric("Weekly Cumulative", f"{weekly_total} Mins")
with m3:
    status = "⚡ LOCKED IN" if today_total >= 120 else "🔌 STANDBY"
    st.metric("System Status", status)

st.markdown("---")

# --- 4. STOPWATCH ENGINE ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Initiate Lock-In")
    task_name = st.text_input("Objective", placeholder="e.g., System Architecture Design")
    
    timer_placeholder = st.empty()
    action_button = st.empty()

    # Session State to track stopwatch
    if 'stopwatch_running' not in st.session_state:
        st.session_state.stopwatch_running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    if not st.session_state.stopwatch_running:
        if action_button.button("🚀 START NEURAL LOCK", use_container_width=True):
            if not task_name:
                st.error("Protocol Error: Objective required.")
            else:
                st.session_state.stopwatch_running = True
                st.session_state.start_time = time.time()
                st.rerun()
    else:
        # Live stopwatch display
        elapsed = int(time.time() - st.session_state.start_time)
        mins, secs = divmod(elapsed, 60)
        timer_placeholder.markdown(f"""
            <div style="text-align: center; border: 2px solid #76b372; padding: 40px; border-radius: 15px; background-color: rgba(118, 179, 114, 0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <h1 style="font-size: 100px; color: #76b372; margin: 0; font-family: 'Courier New', monospace;">{mins:02d}:{secs:02d}</h1>
                <p style="color: #76b372; letter-spacing: 5px; text-transform: uppercase; font-weight: bold;">LOCKED ON: {task_name}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if action_button.button("🛑 STOP & LOCK OUT", use_container_width=True):
            duration_mins = max(1, elapsed // 60)
            execute_query("INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, %s)", 
                          (user, task_name, duration_mins, today_date))
            st.session_state.stopwatch_running = False
            st.session_state.start_time = None
            st.success(f"Session Logged: {duration_mins} Mins")
            time.sleep(1)
            st.rerun()
        
        # Forces the stopwatch to refresh every second
        time.sleep(1)
        st.rerun()

with col_right:
    st.subheader("Neural Log (Today)")
    sessions = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s ORDER BY id DESC", (user, today_date))
    if sessions:
        df_sessions = pd.DataFrame(sessions, columns=["Objective", "Duration (Min)"])
        st.dataframe(df_sessions, use_container_width=True, hide_index=True)
    else:
        st.info("System idle. No sessions logged today.")

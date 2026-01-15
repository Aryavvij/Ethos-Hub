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
st.caption("Active Focus & Cognitive Intensity Tracker")

# --- 3. MOMENTUM METRICS (TOP ROW) ---
today_date = datetime.now().date()
start_of_week = today_date - timedelta(days=today_date.weekday())

# Fetch Totals from focus_sessions table
today_data = fetch_query("SELECT SUM(duration_mins) FROM focus_sessions WHERE user_email=%s AND session_date=%s", (user, today_date))
today_total = today_data[0][0] if today_data[0][0] else 0

weekly_data = fetch_query("SELECT SUM(duration_mins) FROM focus_sessions WHERE user_email=%s AND session_date >= %s", (user, start_of_week))
weekly_total = weekly_data[0][0] if weekly_data[0][0] else 0

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Daily Neural Output", f"{today_total} Mins")
    # Progress bar toward a 2-hour daily goal
    st.progress(min(today_total / 120, 1.0))
with m2:
    st.metric("Weekly Cumulative", f"{weekly_total} Mins")
with m3:
    status = "⚡ LOCKED IN" if today_total >= 120 else "🔌 STANDBY"
    st.metric("System Status", status)

st.markdown("---")

# --- 4. THE LOCK-IN ENGINE ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Initiate Lock-In")
    task_name = st.text_input("Objective", placeholder="e.g., Database Schema Design")
    duration = st.number_input("Duration (Minutes)", min_value=1, max_value=180, value=25)
    
    timer_placeholder = st.empty()
    button_placeholder = st.empty()

    if button_placeholder.button("START NEURAL LOCK", use_container_width=True):
        if not task_name:
            st.error("Protocol Error: Objective required.")
        else:
            button_placeholder.empty() # Hide button
            seconds = duration * 60
            
            # THE COUNTDOWN LOOP
            for t in range(seconds, -1, -1):
                mins, secs = divmod(t, 60)
                timer_placeholder.markdown(f"""
                    <div style="text-align: center; border: 2px solid #76b372; padding: 40px; border-radius: 15px; background-color: rgba(118, 179, 114, 0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <h1 style="font-size: 100px; color: #76b372; margin: 0; font-family: 'Courier New', monospace;">{mins:02d}:{secs:02d}</h1>
                        <p style="color: #76b372; letter-spacing: 5px; text-transform: uppercase; font-weight: bold;">LOCKED ON: {task_name}</p>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
            
            # LOG TO DB
            execute_query("INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, %s)", 
                          (user, task_name, duration, today_date))
            
            st.balloons()
            st.success("Session Data Logged Successfully.")
            time.sleep(2)
            st.rerun()

with col_right:
    st.subheader("Neural Log (Today)")
    sessions = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s ORDER BY id DESC", (user, today_date))
    
    if sessions:
        # Convert to DataFrame for a clean wide-screen look
        df_sessions = pd.DataFrame(sessions, columns=["Objective", "Duration (Min)"])
        st.dataframe(df_sessions, use_container_width=True, hide_index=True)
    else:
        st.info("System idle. No sessions logged today.")

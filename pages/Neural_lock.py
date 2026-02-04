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
    st.switch_page("Home.py") 
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

# --- ANALYTICS ENGINE ---
c_sel1, c_sel2 = st.columns([2, 1])
with c_sel1:
    month_names = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    selected_month_name = st.selectbox("View History", month_names, index=now.month-1)
    month_num = month_names.index(selected_month_name) + 1
with c_sel2:
    selected_year = st.selectbox("Year", [2025, 2026, 2027], index=1)

monthly_raw = fetch_query("""
    SELECT EXTRACT(DAY FROM session_date) as day, SUM(duration_mins) 
    FROM focus_sessions 
    WHERE user_email=%s 
    AND EXTRACT(MONTH FROM session_date) = %s 
    AND EXTRACT(YEAR FROM session_date) = %s
    GROUP BY day ORDER BY day
""", (user, month_num, selected_year))


m_df = pd.DataFrame(monthly_raw, columns=["Day", "Mins"])
m_df["Hours"] = m_df["Mins"] / 60.0

# --- VISUAL MOMENTUM ---
if not m_df.empty:
    fig_m = px.area(m_df, x="Day", y="Hours", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig_m.update_layout(
        height=250, margin=dict(l=0, r=0, t=10, b=0), 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title="Day", range=[1, 31]), 
        yaxis=dict(showgrid=True, title="Total Hours")
    )
    st.plotly_chart(fig_m, use_container_width=True)

st.markdown("---")

# --- PERSISTENT STOPWATCH ENGINE ---
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
                <h1 style="font-size: 60px; color: #444; margin: 0; font-family: monospace;">00:00:00</h1>
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
        hours, remainder = divmod(elapsed_seconds, 3600)
        mins, secs = divmod(remainder, 60)

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

# --- SESSION LOG & FORMATTING ---
with col_log:
    st.subheader("Today's Log")
    today_data = fetch_query("""
        SELECT id, task_name, duration_mins 
        FROM focus_sessions 
        WHERE user_email=%s AND session_date = CURRENT_DATE 
        ORDER BY id DESC
    """, (user,))
    
    if today_data:
        log_df = pd.DataFrame(today_data, columns=["ID", "Objective", "Duration"])
        
        def format_duration(m):
            h, rem = divmod(m, 60)
            if h > 0:
                return f"{int(h)}h {int(rem)}m"
            return f"{int(rem)}m"

        log_df["Time Spent"] = log_df["Duration"].apply(format_duration)

        st.dataframe(
            log_df[["Objective", "Time Spent"]], 
            use_container_width=True, 
            hide_index=True
        )
        
        with st.expander("Delete Session"):
            session_options = {f"{row[1]} ({format_duration(row[2])})": row[0] for row in today_data}
            to_delete = st.selectbox("Select session to remove", options=list(session_options.keys()))
            if st.button("Confirm Delete", use_container_width=True):
                execute_query("DELETE FROM focus_sessions WHERE id=%s", (session_options[to_delete],))
                st.rerun()
    else:
        st.caption("No sessions logged today.")

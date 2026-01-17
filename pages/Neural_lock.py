import streamlit as st
import time
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime, timedelta

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Neural Lock", page_icon="🔒")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

# --- 2. DATA ENGINE ---
# Fetch daily totals for the current month for the Momentum Graph
monthly_raw = fetch_query("""
    SELECT EXTRACT(DAY FROM session_date) as day, SUM(duration_mins) 
    FROM focus_sessions 
    WHERE user_email=%s AND EXTRACT(MONTH FROM session_date) = EXTRACT(MONTH FROM CURRENT_DATE)
    GROUP BY day ORDER BY day
""", (user,))
m_df = pd.DataFrame(monthly_raw, columns=["Day", "Mins"])

st.title("🔒 Neural Lock")
st.caption("High-Intensity Focus Engine")

# --- 3. OVERVIEW METRICS ---
m1, m2, m3 = st.columns(3)
with m1:
    today_mins = m_df[m_df["Day"] == datetime.now().day]["Mins"].sum()
    st.metric("Focus Today", f"{int(today_mins)}m")
with m2:
    month_avg = int(m_df["Mins"].mean()) if not m_df.empty else 0
    st.metric("Monthly Daily Avg", f"{month_avg}m")
with m3:
    status = "🔴 IDLE" if 'stopwatch_start' not in st.session_state or st.session_state.stopwatch_start is None else "🟢 LOCKED IN"
    st.metric("System Status", status)

# --- 4. MONTHLY MOMENTUM GRAPH ---
st.subheader("🌊 Monthly Focus Momentum")
if not m_df.empty:
    fig_m = px.area(m_df, x="Day", y="Mins", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig_m.update_layout(
        height=250, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title="Day of Month"), yaxis=dict(showgrid=True, title="Minutes")
    )
    st.plotly_chart(fig_m, use_container_width=True)
else:
    st.info("Initiate focus sessions to visualize monthly momentum.")

st.markdown("---")

# --- 5. THE ENGINE ROOM (STOPWATCH & DAILY LOG) ---
col_timer, col_log = st.columns([1.2, 1], gap="large")

with col_timer:
    st.subheader("🚀 Focus Session")
    task_name = st.text_input("Objective", placeholder="What are you crushing right now?", label_visibility="collapsed")
    
    timer_placeholder = st.empty()
    action_placeholder = st.empty()

    if 'stopwatch_start' not in st.session_state:
        st.session_state.stopwatch_start = None

    if st.session_state.stopwatch_start is None:
        timer_placeholder.markdown("""
            <div style="text-align: center; border: 2px solid #333; padding: 40px; border-radius: 15px; background: rgba(255, 255, 255, 0.02);">
                <h1 style="font-size: 60px; color: #444; margin: 0; font-family: monospace;">00:00</h1>
                <p style="color: #666; letter-spacing: 2px;">READY TO INITIATE</p>
            </div>
        """, unsafe_allow_html=True)
        
        if action_placeholder.button("⚡ INITIATE NEURAL LOCK", use_container_width=True):
            if not task_name: st.error("Define an objective first.")
            else:
                st.session_state.stopwatch_start = time.time()
                st.rerun()
    else:
        if action_placeholder.button("🛑 STOP & LOG SESSION", use_container_width=True):
            elapsed = int(time.time() - st.session_state.stopwatch_start)
            duration_mins = max(1, elapsed // 60)
            execute_query(
                "INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, CURRENT_DATE)",
                (user, task_name, duration_mins)
            )
            st.session_state.stopwatch_start = None
            st.rerun()

        while st.session_state.stopwatch_start is not None:
            elapsed = int(time.time() - st.session_state.stopwatch_start)
            mins, secs = divmod(elapsed, 60)
            timer_placeholder.markdown(f"""
                <div style="text-align: center; border: 2px solid #76b372; padding: 40px; border-radius: 15px; background: rgba(118, 179, 114, 0.05);">
                    <h1 style="font-size: 60px; color: #76b372; margin: 0; font-family: monospace;">{mins:02d}:{secs:02d}</h1>
                    <p style="color: #76b372; letter-spacing: 5px; font-weight: bold;">LOCKED ON: {task_name.upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

with col_log:
    st.subheader("📋 Today's Logged Sessions")
    today_data = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = CURRENT_DATE ORDER BY id DESC", (user,))
    if today_data:
        st.dataframe(pd.DataFrame(today_data, columns=["Task", "Minutes"]), use_container_width=True, hide_index=True)
    else:
        st.caption("No sessions logged today.")

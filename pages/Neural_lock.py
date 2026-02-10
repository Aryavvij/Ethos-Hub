import streamlit as st
import time
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime as dt, timedelta
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Neural Lock", page_icon="🔒")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
now = dt.now()
t_date = now.date()
st.title("🔒 Neural Lock")
st.caption(f"Protocol Active for {t_date.strftime('%A, %b %d, %Y')}")
g
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    .timer-card {
        text-align: center; 
        border: 2px solid #333; 
        padding: 40px; 
        border-radius: 15px; 
        background: rgba(255, 255, 255, 0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. TOP ANALYTICS OVERVIEW BAR ---
stats_query = fetch_query("""
    WITH daily_totals AS (
        SELECT session_date, SUM(duration_mins) as total_mins
        FROM focus_sessions
        WHERE user_email = %s
        GROUP BY session_date
    )
    SELECT 
        (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
         WHERE user_email = %s AND session_date = CURRENT_DATE) as today,
        (SELECT COALESCE(AVG(total_mins), 0) FROM daily_totals) as daily_avg,
        (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
         WHERE user_email = %s AND session_date >= DATE_TRUNC('week', CURRENT_DATE)) as week_total,
        (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
         WHERE user_email = %s AND session_date >= DATE_TRUNC('month', CURRENT_DATE)) as month_total
""", (user, user, user, user))

s = stats_query[0] if stats_query else (0, 0, 0, 0)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Today's Focus", f"{int(s[0] or 0)}m")
m2.metric("Daily Average", f"{int(s[1] or 0)}m")
m3.metric("Weekly Total", f"{(s[2] or 0)/60:.1f}h")
m4.metric("Monthly Total", f"{(s[3] or 0)/60:.1f}h")

# --- 2. ANALYTICS ENGINE (GRAPH) ---
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

if not m_df.empty:
    fig_m = px.area(m_df, x="Day", y="Hours", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig_m.update_layout(
        height=220, margin=dict(l=0, r=0, t=10, b=0), 
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, range=[1, 31]), 
        yaxis=dict(showgrid=True)
    )
    st.plotly_chart(fig_m, use_container_width=True)

st.markdown("---")

# --- 3. THE FRAGMENTED TIMER ENGINE ---
@st.fragment(run_every="1s")
def timer_fragment():
    col_timer, col_log = st.columns([1.2, 1], gap="large")
    active = fetch_query("SELECT task_name, start_time, is_paused, accumulated_seconds FROM active_sessions WHERE user_email=%s", (user,))

    with col_timer:
        st.subheader("Focus Session")
        if not active:
            task_input = st.text_input("Objective", placeholder="What are you crushing?", key="new_task", label_visibility="collapsed")
            st.markdown('<div class="timer-card"><h1 style="font-size: 60px; color: #444; margin: 0;">00:00:00</h1><p style="color: #666;">READY</p></div>', unsafe_allow_html=True)
            
            if st.button("INITIATE STOPWATCH", use_container_width=True, type="primary"):
                if task_input:
                    execute_query("INSERT INTO active_sessions (user_email, task_name, start_time, is_paused, accumulated_seconds) VALUES (%s, %s, %s, %s, %s)", 
                                  (user, task_input, dt.now(), False, 0))
                    st.rerun()
        else:
            task_name, start_time, is_paused, acc_sec = active[0]
            elapsed = acc_sec if is_paused else int((dt.now() - start_time).total_seconds()) + acc_sec
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            
            color = "#ffaa00" if is_paused else "#76b372"
            st.markdown(f"""
                <div style="text-align: center; border: 2px solid {color}; padding: 40px; border-radius: 15px; background: rgba(118, 179, 114, 0.05);">
                    <h1 style="font-size: 60px; color: {color}; margin: 0; font-family: monospace;">{h:02d}:{m:02d}:{s:02d}</h1>
                    <p style="color: {color}; letter-spacing: 5px; font-weight: bold;">{"PAUSED" if is_paused else "LOCKED ON"}: {task_name.upper()}</p>
                </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2)
            if not is_paused:
                if b1.button("PAUSE", use_container_width=True):
                    execute_query("UPDATE active_sessions SET is_paused=True, accumulated_seconds=%s WHERE user_email=%s", (elapsed, user))
                    st.rerun()
            else:
                if b1.button("RESUME", use_container_width=True):
                    execute_query("UPDATE active_sessions SET is_paused=False, start_time=%s WHERE user_email=%s", (dt.now(), user))
                    st.rerun()

            if b2.button("🛑 STOP & LOG", use_container_width=True):
                duration = max(1, elapsed // 60)
                execute_query("INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, CURRENT_DATE)", (user, task_name, duration))
                execute_query("DELETE FROM active_sessions WHERE user_email=%s", (user,))
                st.rerun()

    with col_log:
        st.subheader("Focus Logs")
        log_date = st.date_input("Date", dt.now().date())
        today_data = fetch_query("SELECT id, task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = %s ORDER BY id DESC", (user, log_date))
        
        if today_data:
            log_df = pd.DataFrame(today_data, columns=["ID", "Objective", "Duration"])
            log_df["Spent"] = log_df["Duration"].apply(lambda m: f"{m//60}h {m%60}m" if m>=60 else f"{m}m")
            st.dataframe(log_df[["Objective", "Spent"]], use_container_width=True, hide_index=True)
            
            if st.button("Clear History (Today)", key="clear_logs"):
                execute_query("DELETE FROM focus_sessions WHERE user_email=%s AND session_date=CURRENT_DATE", (user,))
                st.rerun()
        else:
            st.caption("No logs for this date.")

timer_fragment()

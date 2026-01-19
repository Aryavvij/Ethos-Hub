import streamlit as st
import time
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Neural Lock", page_icon="🔒")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

# --- 2. AUTOMATIC DATE RECOGNITION ---
# This ensures the UI is always aware of the "Now"
now = datetime.now()
t_date = now.date()
st.title("🔒 Neural Lock")
st.caption(f"Protocol Active for {t_date.strftime('%A, %b %d, %Y')}")

# --- 3. MONTHLY SELECTOR ENGINE ---
c_sel1, c_sel2 = st.columns([2, 1])
with c_sel1:
    month_names = ["January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    selected_month_name = st.selectbox("View History", month_names, index=now.month-1)
    month_num = month_names.index(selected_month_name) + 1
with c_sel2:
    selected_year = st.selectbox("Year", [2025, 2026, 2027], index=1)

# --- 4. DATA ENGINE (The "Day Recognition" Logic) ---
monthly_raw = fetch_query("""
    SELECT EXTRACT(DAY FROM session_date) as day, SUM(duration_mins) 
    FROM focus_sessions 
    WHERE user_email=%s 
    AND EXTRACT(MONTH FROM session_date) = %s 
    AND EXTRACT(YEAR FROM session_date) = %s
    GROUP BY day ORDER BY day
""", (user, month_num, selected_year))

m_df = pd.DataFrame(monthly_raw, columns=["Day", "Mins"])

# --- 5. OVERVIEW METRICS ---
m1, m2, m3 = st.columns(3)
with m1:
    # AUTO-RECOGNITION: Checks if viewing today's month/year
    if month_num == now.month and selected_year == now.year:
        today_mins = m_df[m_df["Day"] == now.day]["Mins"].sum()
        st.metric("Focus Today", f"{int(today_mins)}m")
    else:
        month_total = m_df["Mins"].sum()
        st.metric(f"Total Focus ({selected_month_name[:3]})", f"{int(month_total)}m")
        
with m2:
    month_avg = int(m_df["Mins"].mean()) if not m_df.empty else 0
    st.metric("Monthly Daily Avg", f"{month_avg}m")
with m3:
    status = "🔴 IDLE" if 'stopwatch_start' not in st.session_state or st.session_state.stopwatch_start is None else "🟢 LOCKED IN"
    st.metric("System Status", status)

# --- 6. MONTHLY MOMENTUM GRAPH ---
if not m_df.empty:
    fig_m = px.area(m_df, x="Day", y="Mins", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig_m.update_layout(
        height=250, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title="Day", tickmode='linear', dtick=5, range=[1, 31]), 
        yaxis=dict(showgrid=True, title="Minutes")
    )
    st.plotly_chart(fig_m, use_container_width=True)

st.markdown("---")

# --- 7. THE ENGINE ROOM (STOPWATCH) ---
col_timer, col_log = st.columns([1.2, 1], gap="large")

with col_timer:
    st.subheader("🚀 Focus Session")
    task_name = st.text_input("Objective", placeholder="What are you crushing right now?", label_visibility="collapsed")
    
    timer_placeholder = st.empty()
    action_placeholder = st.empty()

    if 'stopwatch_start' not in st.session_state:
        st.session_state.stopwatch_start = None

    if st.session_state.stopwatch_start is None:
        timer_placeholder.markdown(f"""
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
        # DATA LOGGING: explicitly uses CURRENT_DATE for recognition
        if action_placeholder.button("🛑 STOP & LOG SESSION", use_container_width=True):
            elapsed = int(time.time() - st.session_state.stopwatch_start)
            duration_mins = max(1, elapsed // 60)
            execute_query(
                "INSERT INTO focus_sessions (user_email, task_name, duration_mins, session_date) VALUES (%s, %s, %s, CURRENT_DATE)",
                (user, task_name, duration_mins)
            )
            st.session_state.stopwatch_start = None
            st.rerun()

        # Stopwatch Display
        elapsed = int(time.time() - st.session_state.stopwatch_start)
        mins, secs = divmod(elapsed, 60)
        timer_placeholder.markdown(f"""
            <div style="text-align: center; border: 2px solid #76b372; padding: 40px; border-radius: 15px; background: rgba(118, 179, 114, 0.05);">
                <h1 style="font-size: 60px; color: #76b372; margin: 0; font-family: monospace;">{mins:02d}:{secs:02d}</h1>
                <p style="color: #76b372; letter-spacing: 5px; font-weight: bold;">LOCKED ON: {task_name.upper()}</p>
            </div>
        """, unsafe_allow_html=True)

with col_log:
    st.subheader("📋 Today's Log")
    # Query recognizes CURRENT_DATE to isolate today's sessions
    today_data = fetch_query("""
        SELECT task_name, duration_mins 
        FROM focus_sessions 
        WHERE user_email=%s AND session_date = CURRENT_DATE 
        ORDER BY id DESC
    """, (user,))
    
    if today_data:
        log_df = pd.DataFrame(today_data, columns=["Objective", "Duration"])
        st.dataframe(log_df, use_container_width=True, hide_index=True,
            column_config={"Duration": st.column_config.NumberColumn("Mins", format="%d m")})
    else:
        st.caption("No sessions logged today.")

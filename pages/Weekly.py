import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. SET WIDE MODE
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user_email

# SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Weekly Planner")

# Date Input
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# 3. WEEKLY GRID
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    with cols[i]:
        # Big Styled Header
        st.markdown(f"""<div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; margin-bottom: 10px;">
            <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small></div>""", unsafe_allow_html=True)
        
        # Input Section
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New Task")
        if st.button("Add Task", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                              (user, i, new_task, start_date, False))
                st.rerun()
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        # Pull tasks from database
        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                            (user, i, start_date))
        
        # Task List Rendering - PERFECT CENTERING FIX
        for tid, tname, tdone in tasks:
            # Ratios [0.1, 0.8, 0.1] lock buttons into centered positions
            c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
            
            with c1:
                if st.button("✔", key=f"done_{tid}", use_container_width=True):
                    execute_query("UPDATE weekly_planner SET is_done=True WHERE id=%s", (tid,))
                    st.rerun()
            
            with c2:
                status_color = "#76b372" if tdone else "#ff4b4b"
                bg_opacity = "rgba(118, 179, 114, 0.2)" if tdone else "rgba(255, 75, 75, 0.1)"
                
                # Height 38px matches standard Streamlit button height for perfect alignment
                st.markdown(f"""
                    <div style="background:{bg_opacity}; color:{status_color}; 
                    border: 1px solid {status_color}; border-radius: 4px; padding: 5px; 
                    text-align: center; font-weight: bold; font-size: 11px; 
                    height: 38px; line-height: 28px; white-space: nowrap; 
                    overflow: hidden; text-overflow: ellipsis;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            
            with c3:
                if st.button("✖", key=f"del_{tid}", use_container_width=True):
                    execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                    st.rerun()

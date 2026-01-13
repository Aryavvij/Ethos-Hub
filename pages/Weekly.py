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

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

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
        if st.button("Add", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)", (user, i, new_task, start_date))
                st.rerun()
        
        st.write("---")
        
        # ALIGNMENT FIX: This negative margin div pulls the first task up to the line
        st.markdown('<div style="margin-top: -25px;"></div>', unsafe_allow_html=True)
        
        # Task List Area
        st.markdown('<div style="height:400px; overflow-y:auto;">', unsafe_allow_html=True)
        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, i, start_date))
        
        for tid, tname, tdone in tasks:
            # 9:1 Ratio for tight alignment
            t_col, d_col = st.columns([0.85, 0.15])
            
            with t_col:
                # Checkbox for task
                is_checked = st.checkbox(tname, value=bool(tdone), key=f"chk_{tid}")
                if is_checked != bool(tdone):
                    execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (is_checked, tid))
                    st.rerun()
            
            with d_col:
                # Small 'x' to delete
                st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True) # Aligns 'x' with checkbox text
                if st.button("×", key=f"del_{tid}"):
                    execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide", page_title="Weekly Planner")

# Load CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("🗓️ Weekly Planner")

# --- DATE LOGIC ---
today = datetime.now().date()
# Automatically find the Monday of the current week to fix alignment
default_monday = today - timedelta(days=today.weekday())

c1, c2 = st.columns([1, 1])
with c1:
    # Users can pick a date, but it defaults to the current Monday
    start_date = st.date_input("Week Starting On (Monday):", default_monday)
with c2:
    st.markdown(f'<div class="custom-view-bar"><p style="text-align:right; font-size:20px; color:gray;">Viewing: {start_date.strftime("%B %Y")}</p></div>', unsafe_allow_html=True)

user = st.session_state.user_email

# --- ALIGNMENT FIX: Start list with Monday ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    # Calculate the exact date for this specific column
    this_day_date = start_date + timedelta(days=i)
    
    with cols[i]:
        # Header Styling
        st.markdown(f"""
            <div style="background-color: #76b372; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                <p style="margin:0; font-weight:bold; color:white;">{day_name[:3].upper()}</p>
                <p style="margin:0; font-size:12px; color:white;">{this_day_date.strftime('%d %b')}</p>
            </div>
        """, unsafe_allow_html=True)

        # Task Input
        new_task = st.text_input("Add task", key=f"in_{i}", placeholder="+ Task", label_visibility="collapsed")
        if st.button("Add", key=f"btn_{i}"):
            if new_task:
                execute_query(
                    "INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)",
                    (user, i, new_task, start_date)
                )
                st.rerun()
        
        st.write("---")
        
        # Pull tasks from cloud for this specific date
        db_tasks = fetch_query(
            "SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", 
            (user, i, start_date)
        )
        
        done_count = 0
        if db_tasks:
            for tid, tname, tdone in db_tasks:
                # Task Checkbox
                is_checked = st.checkbox(tname, value=bool(tdone), key=f"chk_{tid}")
                if is_checked != bool(tdone):
                    execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (is_checked, tid))
                    st.rerun()
                if is_checked: 
                    done_count += 1
        
        # Summary Stats for the day
        total_tasks = len(db_tasks)
        not_done = total_tasks - done_count
        st.markdown(f"""
            <div style="margin-top: 10px; border-top: 1px solid #444; padding-top: 10px;">
                <p style="color: #76b372; margin: 0; font-size: 14px;">Done: {done_count}</p>
                <p style="color: #ff4b4b; margin: 0; font-size: 14px;">Pending: {not_done}</p>
            </div>
        """, unsafe_allow_html=True)

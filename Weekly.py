import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide", page_title="Weekly Planner")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🗓️ Weekly Planner")

c1, c2 = st.columns([1, 1])
with c1:
    start_date = st.date_input("Week Starting On:", datetime.now(), label_visibility="collapsed")
with c2:
    st.markdown(f'<div class="custom-view-bar"><p>Viewing: {start_date.strftime("%B %Y")}</p></div>', unsafe_allow_html=True)

user = st.session_state.user_email
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_day_date = start_date + timedelta(days=i)
    with cols[i]:
        st.markdown(f"""<div style="background-color: #76b372; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                        <p class="day-header">{day_name[:3]}</p>
                        <p class="day-subtext">{this_day_date.strftime('%d %b')}</p></div>""", unsafe_allow_html=True)

        new_task = st.text_input("Add task", key=f"in_{i}", placeholder="+ Task", label_visibility="collapsed")
        if st.button("Add", key=f"btn_{i}"):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)",
                              (user, i, new_task, start_date))
                st.rerun()
        st.write("---")
        
        # pull tasks from cloud
        db_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", 
                               (user, i, start_date))
        
        done_count = 0
        for tid, tname, tdone in db_tasks:
            is_checked = st.checkbox(tname, value=tdone, key=f"chk_{tid}")
            if is_checked != tdone:
                execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (is_checked, tid))
                st.rerun()
            if is_checked: done_count += 1
        
        not_done = len(db_tasks) - done_count
        st.markdown(f"""<div style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px;">
                        <p style="color: #76b372; margin: 0; font-size: 18px;">Completed: {done_count}</p>
                        <p style="color: #ff4b4b; margin: 0; font-size: 18px;">Pending: {not_done}</p></div>""", unsafe_allow_html=True)
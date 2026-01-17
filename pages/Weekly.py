import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user_email

with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Weekly Planner")
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    with cols[i]:
        st.markdown(f"""<div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; margin-bottom: 10px;">
            <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small></div>""", unsafe_allow_html=True)
        
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New Task")
        if st.button("Add Task", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                              (user, i, new_task, start_date, False))
                st.rerun()
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                            (user, i, start_date))
        
        for tid, tname, tdone in tasks:
            # FIX: Tighter ratio so buttons stay under the day header
            c1, c2, c3 = st.columns([0.15, 0.7, 0.15])
            with c1:
                if st.button("✔", key=f"done_{tid}", use_container_width=True):
                    execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (not tdone, tid))
                    st.rerun()
            with c2:
                status_color = "#76b372" if tdone else "#ff4b4b"
                st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.3); color:{status_color}; border: 1px solid {status_color}; 
                    border-radius: 4px; text-align: center; font-weight: bold; font-size: 10px; 
                    height: 35px; line-height: 33px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            with c3:
                if st.button("✖", key=f"del_{tid}", use_container_width=True):
                    execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                    st.rerun()

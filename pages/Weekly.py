import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

st.title("🗓️ Weekly Planner")
user = st.session_state.user_email
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    with cols[i]:
        # Big Styled Header
        st.markdown(f"""<div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white;">
            <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small></div>""", unsafe_allow_html=True)
        
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed")
        if st.button("Add", key=f"btn_{i}", use_container_width=True):
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)", (user, i, new_task, start_date))
            st.rerun()
        
        st.markdown('<div style="height:300px; overflow-y:auto;">', unsafe_allow_html=True)
        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, i, start_date))
        for tid, tname, tdone in tasks:
            # 9:1 Ratio for Alignment
            t_col, d_col = st.columns([0.9, 0.1])
            is_checked = t_col.checkbox(tname, value=bool(tdone), key=f"chk_{tid}")
            if is_checked != bool(tdone):
                execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (is_checked, tid))
                st.rerun()
            if d_col.button("×", key=f"del_{tid}"):
                execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

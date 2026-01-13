import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

st.title("🗓️ Weekly Planner")
user = st.session_state.user_email
start_date = st.date_input("Week Start (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    with cols[i]:
        st.markdown(f"**{day_name[:3]}**")
        new_task = st.text_input("+", key=f"in_{i}", label_visibility="collapsed")
        if st.button("Add", key=f"btn_{i}"):
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)", (user, i, new_task, start_date))
            st.rerun()

        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, i, start_date))
        for tid, tname, tdone in tasks:
            # ALIGNMENT FIX: 90% text, 10% delete button
            c1, c2 = st.columns([0.9, 0.1])
            c1.checkbox(tname, value=bool(tdone), key=f"chk_{tid}")
            if c2.button("×", key=f"del_{tid}"):
                execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                st.rerun()

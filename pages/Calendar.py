import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

st.title("🗓️ Calendar")
user = st.session_state.user_email
month_num = datetime.now().month
year = 2026

cal_matrix = calendar.monthcalendar(year, month_num)
cols = st.columns(7)
for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                with st.container(border=True):
                    st.write(f"**{day}**")
                    # SYMMETRY FIX: Scrollable div with fixed height
                    st.markdown('<div style="height:80px; overflow-y:auto; overflow-x:hidden;">', unsafe_allow_html=True)
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", (user, f"{year}-{month_num:02d}-{day:02d}"))
                    for eid, desc in events:
                        c1, c2 = st.columns([0.8, 0.2])
                        c1.caption(desc)
                        if c2.button("x", key=f"ev_{eid}"):
                            execute_query("DELETE FROM events WHERE id=%s", (eid,))
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from database import fetch_query, execute_query
from datetime import datetime

# 1. SET WIDE MODE (Must be first)
st.set_page_config(layout="wide", page_title="Weekly Timetable")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    if st.button("Go to Home"): st.switch_page("Home.py")
    st.stop()

user = st.session_state.user_email

st.title("📅 Weekly Timetable")

# 3. SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# 4. TIMETABLE CONTENT
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Wide mode allows us to use more columns comfortably
cols = st.columns(len(days))

for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"#### {day}")
        day_classes = fetch_query("SELECT id, start_time, subject, location FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC", (user, day))
        
        for cid, ctime, csub, cloc in day_classes:
            with st.container(border=True):
                st.markdown(f"**{ctime.strftime('%H:%M')}**")
                st.markdown(f"{csub}")
                st.caption(f"📍 {cloc}")
                if st.button("Delete", key=f"class_{cid}", use_container_width=True):
                    execute_query("DELETE FROM timetable WHERE id=%s", (cid,))
                    st.rerun()

with st.expander("➕ Add Class to Schedule"):
    c1, c2, c3, c4 = st.columns(4)
    day_sel = c1.selectbox("Day", days)
    time_sel = c2.time_input("Start Time")
    sub_sel = c3.text_input("Subject")
    loc_sel = c4.text_input("Location")
    if st.button("Save Class", use_container_width=True):
        execute_query("INSERT INTO timetable (user_email, day_name, start_time, subject, location) VALUES (%s, %s, %s, %s, %s)", (user, day_sel, time_sel, sub_sel, loc_sel))
        st.rerun()

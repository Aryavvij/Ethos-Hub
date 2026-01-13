import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# 1. FIT TO SCREEN (Must be first)
st.set_page_config(layout="wide", page_title="Monthly Events")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    if st.button("Go to Home"): st.switch_page("Home.py")
    st.stop()

user = st.session_state.user_email

# 3. SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Monthly Events")
today = datetime.now()

# 4. MONTH NAME SELECTORS
c1, c2 = st.columns([2, 1])
with c1:
    # Restored: month_name list instead of numbers
    month_names = list(calendar.month_name)[1:] 
    selected_month_name = st.selectbox("Month", month_names, index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028], index=1)

# Convert name back to number for the database/logic
month_num = list(calendar.month_name).index(selected_month_name)

# 5. ADD EVENT
with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event", use_container_width=True):
        if e_desc:
            execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)", (user, e_date, e_desc))
            st.rerun()

# 6. CALENDAR GRID
st.markdown("---")
cal_matrix = calendar.monthcalendar(year, month_num)
day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
header_cols = st.columns(7)

for i, d in enumerate(day_headers):
    header_cols[i].markdown(f"<p style='text-align:center; color:#76b372; font-weight:bold; font-size:18px;'>{d}</p>", unsafe_allow_html=True)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                # SYMMETRY FIX: Fixed height container
                with st.container(border=True):
                    st.markdown(f"**{day}**")
                    
                    # Scrollable area keeps the grid perfectly aligned
                    st.markdown('<div style="height:90px; overflow-y:auto; overflow-x:hidden;">', unsafe_allow_html=True)
                    
                    cur_date = f"{year}-{month_num:02d}-{day:02d}"
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                    
                    for eid, desc in events:
                        # ALIGNMENT FIX: Tight columns for text and delete button
                        ec1, ec2 = st.columns([0.8, 0.2])
                        with ec1:
                            st.markdown(f"<div style='background:#76b372; color:white; padding:3px; border-radius:3px; font-size:10px; margin-bottom:2px;'>{desc}</div>", unsafe_allow_html=True)
                        with ec2:
                            if st.button("×", key=f"del_{eid}"):
                                execute_query("DELETE FROM events WHERE id=%s", (eid,))
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

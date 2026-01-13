import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

with st.sidebar:
    st.success(f"User: {st.session_state.user_email}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

st.title("🗓️ Monthly Events")
today = datetime.now()
user = st.session_state.user_email

# Date Selectors
c1, c2 = st.columns([2, 1])
with c1:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028, 2029, 2030], index=1)
month_num = list(calendar.month_name).index(month_name)

# --- ADD EVENT ---
with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event"):
        execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)", (user, e_date, e_desc))
        st.rerun()

# --- CALENDAR GRID ---
cal_matrix = calendar.monthcalendar(year, month_num)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)
for i, d in enumerate(days):
    cols[i].markdown(f"<p style='text-align:center; color:#76b372; font-weight:bold;'>{d}</p>", unsafe_allow_html=True)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                # SYMMETRY FIX: container with border and fixed scroll height
                with st.container(border=True):
                    st.markdown(f"<p style='margin:0; font-size:12px; font-weight:bold;'>{day}</p>", unsafe_allow_html=True)
                    
                    cur_date = f"{year}-{month_num:02d}-{day:02d}"
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                    
                    # Scrollable div keeps the box size uniform
                    st.markdown('<div style="height:85px; overflow-y:auto; overflow-x:hidden;">', unsafe_allow_html=True)
                    for eid, desc in events:
                        # ALIGNMENT FIX: Use sub-columns for the event text and the X
                        ec1, ec2 = st.columns([0.8, 0.2])
                        with ec1:
                            st.markdown(f"""<div style="background:#76b372; color:white; padding:2px; border-radius:3px; font-size:9px; margin-bottom:2px;">{desc}</div>""", unsafe_allow_html=True)
                        with ec2:
                            if st.button("×", key=f"del_{eid}", help="Delete"):
                                execute_query("DELETE FROM events WHERE id=%s", (eid,))
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

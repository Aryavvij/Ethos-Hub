import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

# --- ISSUE #5: SIDEBAR LOGOUT ---
with st.sidebar:
    st.success(f"User: {st.session_state.user_email}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Monthly Events")

# Date Selectors
today = datetime.now()
c1, c2 = st.columns([2, 1])
with c1:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
with c2:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=today.year)

month_num = list(calendar.month_name).index(month_name)

# --- ADD EVENT ---
with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event"):
        execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)",
                      (st.session_state.user_email, e_date, e_desc))
        st.rerun()

# --- ISSUE #7: SYMMETRICAL CALENDAR GRID ---
cal_matrix = calendar.monthcalendar(year, month_num)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)
for i, d in enumerate(days):
    cols[i].markdown(f"<p style='text-align:center; color:#76b372;'><b>{d}</b></p>", unsafe_allow_html=True)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            with cols[i]:
                # Fixed height container to maintain symmetry
                with st.container(border=True):
                    st.markdown(f"<p style='margin:0; font-size:12px;'>{day}</p>", unsafe_allow_html=True)
                    
                    # Fetch Events
                    cur_date = f"{year}-{month_num:02d}-{day:02d}"
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", 
                                        (st.session_state.user_email, cur_date))
                    
                    # Scrollable event area to prevent box expansion
                    st.markdown('<div style="height:60px; overflow-y:auto; font-size:10px;">', unsafe_allow_html=True)
                    for eid, desc in events:
                        ev_c, del_c = st.columns([4, 1])
                        ev_c.markdown(f"<div style='background:#76b372; color:white; border-radius:3px; padding:2px;'>{desc}</div>", unsafe_allow_html=True)
                        if del_c.button("×", key=f"d_{eid}"):
                            execute_query("DELETE FROM events WHERE id=%s", (eid,))
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

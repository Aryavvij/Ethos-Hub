import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access the calendar.")
    st.stop()

st.set_page_config(layout="wide", page_title="Monthly Calendar")

# Load CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("🗓️ Monthly Events & Birthdays")

# Date Selectors
today = datetime.now()
col_m, col_y = st.columns([2, 1])
with col_m:
    month_name = st.selectbox("Select Month", list(calendar.month_name)[1:], index=today.month-1)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=today.year)

month_num = list(calendar.month_name).index(month_name)

# --- Add Event Section ---
with st.expander("➕ Add New Event"):
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        event_date = st.date_input("Date", datetime(year, month_num, 1))
    with e_col2:
        event_desc = st.text_input("What's happening?")
    
    if st.button("Save Event"):
        if event_desc:
            execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)",
                          (st.session_state.user_email, event_date, event_desc))
            st.success("Event added!")
            st.rerun()

st.write("---")

# --- CALENDAR GRID ---
# Weekday Headers
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
header_cols = st.columns(7)
for idx, day_head in enumerate(days_of_week):
    header_cols[idx].markdown(f"<p style='text-align:center; font-weight:bold; color:#76b372;'>{day_head}</p>", unsafe_allow_html=True)

# Generate month matrix
cal_matrix = calendar.monthcalendar(year, month_num)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            # Empty box for days not in the current month
            cols[i].markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        else:
            with cols[i]:
                # Every day gets a container with a border
                with st.container(border=True):
                    # Day number at the top
                    st.markdown(f"<p style='margin:0; font-weight:bold;'>{day}</p>", unsafe_allow_html=True)
                    
                    # Date string for database query
                    current_date = f"{year}-{month_num:02d}-{day:02d}"
                    
                    # Fetch events for this specific box
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", 
                                        (st.session_state.user_email, current_date))
                    
                    if events:
                        for eid, desc in events:
                            # Small event pills
                            st.markdown(f"""
                                <div style="background-color:#76b372; color:white; font-size:10px; 
                                border-radius:3px; padding:2px 5px; margin-top:2px;">
                                    📍 {desc}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        # Ensures the boxes stay a consistent height even when empty
                        st.write("")

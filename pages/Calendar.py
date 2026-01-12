import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.stop()

st.title("🗓️ Monthly Events & Birthdays")

# Month/Year Selector
today = datetime.now()
col1, col2 = st.columns(2)
with col1:
    month = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
with col2:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=today.year)

month_num = list(calendar.month_name).index(month)

# --- Add New Event ---
with st.expander("➕ Add New Event/Birthday"):
    date_val = st.date_input("Event Date", datetime(year, month_num, 1))
    event_desc = st.text_input("Event Description (e.g., Mom's Birthday)")
    if st.button("Save Event"):
        execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)",
                      (st.session_state.user_email, date_val, event_desc))
        st.success("Saved!")
        st.rerun()

# --- Display Month Grid ---
st.write(f"### {month} {year}")
cal = calendar.monthcalendar(year, month_num)

for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("") # Empty days
        else:
            with cols[i]:
                # Styling for the day box
                st.markdown(f"**{day}**")
                current_date = f"{year}-{month_num:02d}-{day:02d}"
                
                # Fetch events for this specific day from Supabase
                day_events = fetch_query("SELECT description FROM events WHERE user_email=%s AND event_date=%s", 
                                        (st.session_state.user_email, current_date))
                
                for ev in day_events:
                    st.caption(f"📍 {ev[0]}")

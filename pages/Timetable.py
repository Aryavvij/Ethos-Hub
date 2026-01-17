import streamlit as st
from database import fetch_query, execute_query
from datetime import datetime, time

# 1. SET WIDE MODE
st.set_page_config(layout="wide", page_title="Weekly Timetable")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    if st.button("Go to Home"): st.switch_page("Home.py")
    st.stop()

user = st.session_state.user_email

# SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("📅 Weekly Timetable")
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 3. ADD CLASS BAR (iPhone-style Picker Implementation)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

with st.expander("➕ Add Class to Schedule", expanded=False):
    # Top Row: Day and Subject
    r1c1, r1c2, r1c3 = st.columns([1, 2, 1])
    day_sel = r1c1.selectbox("Day", days)
    sub_sel = r1c2.text_input("Subject", placeholder="e.g. Data Structures")
    loc_sel = r1c3.text_input("Location", placeholder="e.g. AB5-201")

    st.write("**Start Time (iPhone Style)**")
    # Bottom Row: The iPhone Picker (Hour, Minute, AM/PM)
    p1, p2, p3 = st.columns([1, 1, 1])
    
    hour_val = p1.selectbox("Hour", [i for i in range(1, 13)], index=7) # Default 8
    min_val = p2.selectbox("Minute", [f"{i:02d}" for i in range(60)], index=50) # Default 50
    period_val = p3.selectbox("AM/PM", ["AM", "PM"], index=0)

    # Convert selection to a 24-hour time object for database storage
    h24 = int(hour_val)
    if period_val == "PM" and h24 != 12: h24 += 12
    if period_val == "AM" and h24 == 12: h24 = 0
    final_time = time(h24, int(min_val))

    if st.button("Save Class", use_container_width=True):
        if sub_sel:
            execute_query("""
                INSERT INTO timetable (user_email, day_name, start_time, subject, location) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user, day_sel, final_time, sub_sel, loc_sel))
            st.rerun()
        else:
            st.error("Please enter a subject.")

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# 4. TIMETABLE CONTENT
cols = st.columns(len(days))

for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"<h4 style='text-align: center; color: #76b372;'>{day[:3].upper()}</h4>", unsafe_allow_html=True)
        day_classes = fetch_query("""
            SELECT id, start_time, subject, location 
            FROM timetable 
            WHERE user_email=%s AND day_name=%s 
            ORDER BY start_time ASC
        """, (user, day))
        
        for cid, ctime, csub, cloc in day_classes:
            with st.container(border=True):
                # Display in 12-hour format with AM/PM
                formatted_time = ctime.strftime('%I:%M %p')
                st.markdown(f"<span style='color:#76b372; font-weight:bold;'>{formatted_time}</span>", unsafe_allow_html=True)
                st.markdown(f"**{csub.upper()}**")
                if cloc:
                    st.caption(f"📍 {cloc}")
                
                if st.button("Delete", key=f"class_{cid}", use_container_width=True):
                    execute_query("DELETE FROM timetable WHERE id=%s", (cid,))
                    st.rerun()

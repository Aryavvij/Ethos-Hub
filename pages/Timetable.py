import streamlit as st
from database import execute_query, fetch_query
import pandas as pd

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.stop()

st.title("Weekly Timetable")

user = st.session_state.user_email
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# --- SECTION 1: ADD/EDIT CLASSES ---
with st.expander("Edit Schedule (Add or Remove Classes)"):
    col1, col2, col3 = st.columns(3)
    with col1:
        day_input = st.selectbox("Day", days)
        time_input = st.time_input("Start Time")
    with col2:
        subject_input = st.text_input("Subject/Class Name")
    with col3:
        loc_input = st.text_input("Location (Room)")
        
    if st.button("Add to Timetable"):
        if subject_input:
            execute_query(
                "INSERT INTO timetable (user_email, day_name, start_time, subject, location) VALUES (%s, %s, %s, %s, %s)",
                (user, day_input, time_input.strftime("%H:%M"), subject_input, loc_input)
            )
            st.success(f"Added {subject_input}!")
            st.rerun()

# --- SECTION 2: VIEW TIMETABLE ---
st.markdown("---")
cols = st.columns(len(days))

for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"""
            <div style="background-color:#76b372; padding:5px; border-radius:5px; text-align:center; margin-bottom:10px;">
                <p style="margin:0; font-weight:bold; color:white;">{day[:3].upper()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Fetch classes for this day sorted by time
        classes = fetch_query(
            "SELECT id, start_time, subject, location FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC",
            (user, day)
        )
        
        if classes:
            for cid, ctime, csub, cloc in classes:
                # Display class info
                with st.container(border=True):
                    st.markdown(f"**{ctime.strftime('%H:%M')}**")
                    st.markdown(f"*{csub}*")
                    if cloc:
                        st.caption(f"📍 {cloc}")
                    
                    # Small delete button for each entry
                    if st.button("🗑️", key=f"del_{cid}"):
                        execute_query("DELETE FROM timetable WHERE id=%s", (cid,))
                        st.rerun()
        else:
            st.caption("No classes")

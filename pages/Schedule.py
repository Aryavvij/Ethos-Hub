import streamlit as st
import pandas as pd
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Schedule Architect", page_icon="🏛️")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("🏛️ Schedule Architect")
st.caption("Synchronized Academic & Personal Time Blocks")

# --- 3. INPUT SECTION (Clean Table Style) ---
with st.expander("➕ Add Schedule Block", expanded=True):
    # Standardized text box sizes
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        day_choice = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    with c2:
        start_t = st.text_input("Start Time", placeholder="e.g. 08:50")
    with c3:
        end_t = st.text_input("End Time", placeholder="e.g. 10:45")
    with c4:
        activity = st.text_input("Task / Class", placeholder="e.g. Data Structures")
    
    if st.button("Architect Block", use_container_width=True):
        if start_t and end_t and activity:
            # Combine for database consistency
            time_range = f"{start_t} - {end_t}"
            execute_query("""
                INSERT INTO master_schedule (user_email, day_name, time_range, activity) 
                VALUES (%s, %s, %s, %s)
            """, (user, day_choice, time_range, activity))
            st.rerun()

st.markdown("---")

# --- 4. THE WEEKLY VIEW (7-Column Professional Table) ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day in enumerate(days):
    with cols[i]:
        # Day Header - Matching your Weekly Planner style
        st.markdown(f"""
            <div style="background:#76b372; padding:10px; border-radius:5px; text-align:center; color:white; margin-bottom: 15px;">
                <strong style="letter-spacing: 2px;">{day[:3].upper()}</strong>
            </div>
        """, unsafe_allow_html=True)
        
        # Pull entries for this day
        # Note: In a real scenario, you'd want a more robust sorting for time_range strings
        day_data = fetch_query("""
            SELECT id, time_range, activity FROM master_schedule 
            WHERE user_email=%s AND day_name=%s ORDER BY time_range ASC
        """, (user, day))
        
        if day_data:
            for sid, trange, task in day_data:
                # Structured Card for each task
                with st.container(border=True):
                    st.markdown(f"<span style='color:#76b372; font-weight:bold; font-size:12px;'>{trange}</span>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 5px 0; font-weight:bold; font-size:13px;'>{task.upper()}</p>", unsafe_allow_html=True)
                    
                    # Minimalist Delete Button
                    if st.button("Delete", key=f"sch_{sid}", use_container_width=True):
                        execute_query("DELETE FROM master_schedule WHERE id=%s", (sid,))
                        st.rerun()
        else:
            st.caption("No blocks defined.")

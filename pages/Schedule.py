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

# CSS: Vertical alignment for the grid
st.markdown("""
    <style>
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .slot-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        height: 80px;
        overflow: hidden;
    }
    .time-header {
        color: #76b372;
        font-weight: bold;
        font-family: monospace;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. INPUT SECTION ---
with st.expander("➕ Add Schedule Block"):
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        day_choice = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    with c2:
        time_frame = st.text_input("Time Frame", placeholder="e.g. 08:50 - 10:45")
    with c3:
        activity = st.text_input("Activity/Class", placeholder="e.g. Data Structures (AB5-201)")
    
    if st.button("Architect Block", use_container_width=True):
        if time_frame and activity:
            execute_query("""
                INSERT INTO master_schedule (user_email, day_name, time_range, activity) 
                VALUES (%s, %s, %s, %s)
            """, (user, day_choice, time_frame, activity))
            st.rerun()

st.markdown("---")

# --- 4. THE 8-COLUMN MASTER GRID ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# 8 Columns: 1 for Time, 7 for Days
grid_cols = st.columns([0.8, 1, 1, 1, 1, 1, 1, 1])

# Column 0: Time Indicators (This shows unique time frames used in your schedule)
with grid_cols[0]:
    st.markdown("<p style='text-align:center; font-weight:bold; color:gray;'>TIME</p>", unsafe_allow_html=True)
    # Fetch all unique time slots across the week to build the vertical axis
    time_slots_raw = fetch_query("SELECT DISTINCT time_range FROM master_schedule WHERE user_email=%s ORDER BY time_range ASC", (user,))
    time_slots = [t[0] for t in time_slots_raw]
    
    for slot in time_slots:
        st.markdown(f"""
            <div style="height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <span class="time-header">{slot}</span>
            </div>
        """, unsafe_allow_html=True)

# Columns 1-7: The Days
for i, day in enumerate(days):
    with grid_cols[i+1]:
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:#76b372;'>{day[:3].upper()}</p>", unsafe_allow_html=True)
        
        for slot in time_slots:
            # Find the activity for this specific day and time slot
            entry = fetch_query("""
                SELECT id, activity FROM master_schedule 
                WHERE user_email=%s AND day_name=%s AND time_range=%s
            """, (user, day, slot))
            
            if entry:
                eid, desc = entry[0]
                st.markdown(f"""
                    <div class="slot-box" style="border-left: 4px solid #76b372;">
                        <p style="margin:0; font-size:11px; font-weight:bold;">{desc.upper()}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{day}_{slot}", use_container_width=True):
                    execute_query("DELETE FROM master_schedule WHERE id=%s", (eid,))
                    st.rerun()
            else:
                # Empty slot placeholder to maintain grid alignment
                st.markdown('<div class="slot-box" style="border: 1px dashed #333; opacity: 0.3;"></div>', unsafe_allow_html=True)

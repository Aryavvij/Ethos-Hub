import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. SET WIDE MODE & PAGE CONFIG
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

# --- CSS: BOLD SYMMETRY & LARGE PROGRESS RING ---
st.markdown("""
    <style>
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 0 10px !important;
    }
    
    /* PROGRESS RING: Matches Column Width */
    .progress-wrapper {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 15px 0;
    }
    .circular-chart {
        display: block;
        width: 100%; /* Forces it to match day block width */
        max-width: 120px; /* Upper limit for very wide screens */
    }
    .circle-bg {
        fill: none;
        stroke: #333;
        stroke-width: 2.5;
    }
    .circle {
        fill: none;
        stroke-width: 2.5;
        stroke-linecap: round;
        transition: stroke-dasharray 0.6s ease 0s;
        stroke: #76b372;
    }
    .percentage {
        fill: #76b372;
        font-family: sans-serif;
        font-size: 0.55em;
        text-anchor: middle;
        font-weight: bold;
    }
    
    /* Input & Button styling remains locked to 35px */
    .stCheckbox, .stButton, div[data-testid="stMarkdownContainer"] {
        height: 35px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("🗓️ Weekly Planner")

# Date Input
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# 3. WEEKLY GRID (7 Columns for 7 Days)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    
    # FETCH DATA FOR PROGRESS
    tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t[2])
    progress_pct = int((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    with cols[i]:
        # DAY HEADER BLOCK
        st.markdown(f"""
            <div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; width:100%; box-sizing:border-box;">
                <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # --- LARGE CENTRAL PROGRESS RING ---
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{progress_pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" class="percentage">{progress_pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # New Task Input
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New Task")
        if st.button("Add Task", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                              (user, i, new_task, start_date, False))
                st.rerun()
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        # --- TASK LIST: 70:30 SPLIT ---
        for tid, tname, tdone in tasks:
            c_left, c_right = st.columns([0.7, 0.3])
            
            with c_left:
                status_color = "#76b372" if tdone else "#ff4b4b"
                bg_opacity = "rgba(118, 179, 114, 0.2)" if tdone else "rgba(255, 75, 75, 0.1)"
                
                st.markdown(f"""
                    <div style="background:{bg_opacity}; color:{status_color}; border: 1px solid {status_color}; 
                    border-radius: 4px; text-align: center; font-weight: bold; font-size: 10px; 
                    height: 35px; line-height: 33px; width: 100%; white-space: nowrap; 
                    padding: 0 5px; overflow: hidden; text-overflow: ellipsis; box-sizing: border-box;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            
            with c_right:
                if st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed"):
                    if not tdone:
                        execute_query("UPDATE weekly_planner SET is_done=True WHERE id=%s", (tid,))
                        st.rerun()
                else:
                    if tdone:
                        execute_query("UPDATE weekly_planner SET is_done=False WHERE id=%s", (tid,))
                        st.rerun()

        if tasks:
            if st.button("🗑️", key=f"clr_{i}", help=f"Clear {day_name}"):
                execute_query("DELETE FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, i, start_date))
                st.rerun()

import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. SET WIDE MODE & PAGE CONFIG
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

# --- CSS: ABSOLUTE SYMMETRY & OVERLAP FIX ---
st.markdown("""
    <style>
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    
    /* Lock the Progress Ring Space */
    .progress-wrapper {
        width: 100%;
        height: 110px; 
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 5px;
    }
    
    .circular-chart { width: 85px; height: 85px; }
    .circle-bg { fill: none; stroke: #333; stroke-width: 2.8; }
    .circle { fill: none; stroke-width: 2.8; stroke-linecap: round; stroke: #76b372; }
    .percentage { fill: #76b372; font-family: sans-serif; font-size: 0.55em; text-anchor: middle; font-weight: bold; }

    /* Task Row Styling */
    .task-container {
        width: 100%;
        margin-top: 10px;
    }
    
    /* Standardize Button Heights */
    .stButton > button {
        height: 32px !important;
        padding: 0px !important;
        font-size: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

# SIDEBAR
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Weekly Planner")

# Date Input (Auto-calculated to the current Monday)
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

# 3. WEEKLY GRID (7 Columns for 7 Days)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    
    # FETCH TASKS
    tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t[2])
    progress_pct = int((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    with cols[i]:
        # DAY HEADER
        st.markdown(f"""
            <div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; width:100%; box-sizing:border-box;">
                <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # PROGRESS RING
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{progress_pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" class="percentage">{progress_pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # INPUT AREA
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New Task")
        if st.button("Add Task", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                              (user, i, new_task, start_date, False))
                st.rerun()
        
        st.markdown("<hr style='margin:10px 0; border:0.5px solid #333;'>", unsafe_allow_html=True)
        
        # --- TASK LIST: TWO COLUMN TABLE LOGIC ---
        for tid, tname, tdone in tasks:
            # Column 1 (Task Text) | Column 2 (Finish Button)
            t_col, b_col = st.columns([0.65, 0.35])
            
            with t_col:
                # Styled box for the Task Text
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); color:white; border: 1px solid #444; 
                    border-radius: 4px; text-align: left; font-size: 11px; height: 32px; 
                    line-height: 30px; padding: 0 8px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            
            with b_col:
                # The Finish Button: Deletes task upon press to clear the board
                if st.button("FINISH", key=f"fin_{tid}", use_container_width=True):
                    execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                    st.rerun()

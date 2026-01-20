import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

render_sidebar()

# --- CSS: ABSOLUTE GRID LOCK ---
st.markdown("""
    <style>
    /* 1. Fix the Column Widths and prevent vertical drifting */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        min-width: 0px !important;
    }

    /* 2. Progress Circle: Fixed Space Lock */
    .progress-wrapper {
        width: 100%;
        height: 100px; 
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    .circular-chart { width: 80px; height: 80px; }
    .circle-bg { fill: none; stroke: #333; stroke-width: 2.8; }
    .circle { fill: none; stroke-width: 2.8; stroke-linecap: round; stroke: #76b372; }
    .percentage { fill: #76b372; font-family: sans-serif; font-size: 0.55em; text-anchor: middle; font-weight: bold; }

    /* 3. TASK ROW: The "Table Row" look */
    .task-row-container {
        display: flex;
        align-items: center;
        width: 100%;
        height: 40px;
        margin-bottom: 5px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        border: 1px solid #444;
    }
    
    /* 4. Input Field Normalization */
    input {
        font-size: 12px !important;
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

# 3. WEEKLY GRID
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    
    # FETCH DATA
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
        
        # ADD TASK SECTION (Single unit to prevent misalignment)
        with st.container():
            new_task = st.text_input("Add", key=f"in_{i}", label_visibility="collapsed", placeholder="+ Task")
            if st.button("ADD", key=f"btn_{i}", use_container_width=True):
                if new_task:
                    execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                                  (user, i, new_task, start_date, False))
                    st.rerun()

        st.markdown("<hr style='margin:10px 0; border:0.5px solid #333;'>", unsafe_allow_html=True)
        
        # --- THE TASK LIST ---
        for tid, tname, tdone in tasks:
            # We use a single container to hold both text and checkbox to avoid column-splitting bugs
            status_color = "#76b372" if tdone else "#ff4b4b"
            
            # Using Markdown for the name and a checkbox right next to it
            # To ensure they never split, we place them in a small container
            with st.container(border=True):
                # We show the name and a checkbox. Clicking the checkbox updates the DB.
                # Label is the task name to save space
                if st.checkbox(tname.upper(), value=tdone, key=f"chk_{tid}"):
                    if not tdone:
                        execute_query("UPDATE weekly_planner SET is_done=True WHERE id=%s", (tid,))
                        st.rerun()
                else:
                    if tdone:
                        execute_query("UPDATE weekly_planner SET is_done=False WHERE id=%s", (tid,))
                        st.rerun()

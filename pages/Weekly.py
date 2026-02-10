import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar

st.set_page_config(layout="wide", page_title="Weekly Planner", page_icon="🗓️")

# --- GATEKEEPER ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- CSS STYLING (The Alignment Fix) ---
st.markdown("""
    <style>
    /* 1. Force checkbox and text to share a horizontal centerline */
    [data-testid="stCheckbox"] {
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stCheckbox"] > label {
        display: flex !important;
        align-items: center !important;
        margin-bottom: 0px !important;
    }

    /* 2. Slim down the container padding for the 7-day grid */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 2px !important;
        padding-bottom: 2px !important;
    }

    /* 3. Circular Progress Chart Styling */
    .progress-wrapper {
        display: flex;
        justify-content: center;
        padding: 10px 0;
    }
    .circular-chart {
        display: block;
        margin: 10px auto;
        max-width: 55px;
        max-height: 55px;
    }
    .circle-bg { fill: none; stroke: #333; stroke-width: 3.8; }
    .circle { fill: none; stroke-width: 2.8; stroke: #76b372; stroke-linecap: round; transition: stroke-dasharray 0.3s ease; }
    
    /* 4. Task Row optical centering */
    .task-text {
        margin: 0 !important; 
        font-size: 11px !important; 
        font-weight: bold !important; 
        line-height: 1.2 !important;
        padding-top: 3px; /* Micro-adjustment to center text with checkbox */
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Weekly Planner")

# --- THE TASK ARCHITECT (CENTRAL HUB) ---
with st.expander("TASK ARCHITECT (Manage Week)", expanded=False):
    c1, c2 = st.columns([1, 2])
    target_day = c1.selectbox("Select Day", days)
    day_idx = days.index(target_day)
    task_input = c2.text_input("New Task Description", placeholder="Enter task name here...")
    
    existing_tasks = fetch_query("SELECT id, task_name FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, day_idx, start_date))
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    if btn_col1.button("ADD TASK", use_container_width=True, type="primary"):
        if task_input:
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, False)", (user, day_idx, task_input, start_date))
            st.rerun()

    if existing_tasks:
        task_list = {t[1]: t[0] for t in existing_tasks}
        selected_task_name = st.selectbox("Existing Tasks for " + target_day, options=list(task_list.keys()))
        selected_id = task_list[selected_task_name]
        
        if btn_col2.button("RENAME TASK", use_container_width=True):
            if task_input:
                execute_query("UPDATE weekly_planner SET task_name=%s WHERE id=%s", (task_input, selected_id))
                st.rerun()
                
        if btn_col3.button("DELETE TASK", use_container_width=True):
            execute_query("DELETE FROM weekly_planner WHERE id=%s", (selected_id,))
            st.rerun()


# --- 7-DAY GRID RENDERING ---

cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    day_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total = len(day_tasks)
    done = sum(1 for t in day_tasks if t[2])
    pct = int((done / total * 100)) if total > 0 else 0
    
    with cols[i]:
        # Day Header
        st.markdown(f"""
            <div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; width:100%; box-sizing:border-box;">
                <strong style="font-size: 13px;">{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Circular Progress Chart
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" style="fill:#76b372; font-size:9px; text-anchor:middle; font-weight:bold;">{pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # Task Execution List
        for tid, tname, tdone in day_tasks:
            with st.container(border=True):
                t_c1, t_c2 = st.columns([0.25, 0.75])
                
                with t_c1:
                    new_val = st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed")
                    if new_val != tdone:
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (new_val, tid))
                        try:
                            from services import invalidate_user_caches
                            invalidate_user_caches()
                        except: pass
                        st.rerun()
                
                with t_c2:
                    text_style = "text-decoration: line-through; color: #555;" if tdone else "color: white;"
                    st.markdown(f"<p class='task-text' style='{text_style}'>{tname.upper()}</p>", unsafe_allow_html=True)

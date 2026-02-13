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

# --- CSS STYLING ---
st.markdown("""
    <style>
    /* 1. Header Styling */
    .day-header {
        background: #76b372; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center; 
        color: white; 
        margin-bottom: 10px;
        width: 100%; /* Ensures header defines the column width */
    }
    .day-header strong { font-size: 18px !important; display: block; }
    .day-header small { font-size: 14px !important; opacity: 0.9; }

    /* 2. PROGRESS CHART: Matches Header Width & Aligned */
    .progress-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%; 
        padding: 10px 0 20px 0;
    }
    .circular-chart {
        width: 85% !important; /* Scaled to visually match the header box width */
        max-width: 100px;
        height: auto;
    }
    .circle-bg { fill: none; stroke: #333; stroke-width: 3.5; }
    .circle { fill: none; stroke-width: 3.5; stroke: #76b372; stroke-linecap: round; }
    
    /* 3. TASK BOX: The Multi-Line Centering Fix */
    /* This targets the Streamlit container and forces it to be a centered flex row */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0px !important;
    }
    
    /* Force the internal row of the task to center everything vertically */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important; 
        align-items: center !important;
    }

    .task-text {
        font-size: 15px !important; 
        font-weight: 600 !important; 
        line-height: 1.2 !important;
        margin: 0 !important;
        color: white;
        text-align: left;
        width: 100%;
    }

    /* 4. Checkbox Centering */
    div[data-testid="stCheckbox"] {
        margin-bottom: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Weekly Planner")

# --- TASK ARCHITECT ---
with st.expander("TASK ARCHITECT (Manage Week)", expanded=False):
    c1, c2 = st.columns([1, 2])
    target_day = c1.selectbox("Select Day", days)
    day_idx = days.index(target_day)
    task_input = c2.text_input("New Task Description", placeholder="Enter task name...")
    
    existing_tasks = fetch_query("SELECT id, task_name FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, day_idx, start_date))
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    if btn_col1.button("ADD TASK", use_container_width=True):
        if task_input:
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, False)", (user, day_idx, task_input, start_date))
            st.rerun()

# --- 7-DAY GRID ---
cols = st.columns(7, gap="small")

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    day_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total = len(day_tasks)
    done = sum(1 for t in day_tasks if t[2])
    pct = int((done / total * 100)) if total > 0 else 0
    
    with cols[i]:
        st.markdown(f"""
            <div class="day-header">
                <strong>{day_name[:3].upper()}</strong>
                <small>{this_date.strftime('%d %b')}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Circular Progress (Width Aligned)
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" style="fill:#76b372; font-size:10px; text-anchor:middle; font-weight:bold;">{pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # Tasks
        for tid, tname, tdone in day_tasks:
            with st.container(border=True):

                t_c1, t_c2 = st.columns([0.2, 0.8], vertical_alignment="center")
                
                with t_c1:
                    new_val = st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed")
                    if new_val != tdone:
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (new_val, tid))
                        st.rerun()
                
                with t_c2:
                    text_style = "text-decoration: line-through; color: #666;" if tdone else "color: white;"
                    st.markdown(f"<p class='task-text' style='{text_style}'>{tname.upper()}</p>", unsafe_allow_html=True)

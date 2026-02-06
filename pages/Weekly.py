import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner", page_icon="🗓️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- CSS STYLING (THE PRECISION FIX) ---
st.markdown("""
    <style>
    /* 1. Global Column Alignment */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 0px !important;
    }
    
    /* 2. ADD Button Styling */
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }

    /* 3. TRASH BUTTON PRECISION - Shrinking to Checkbox size */
    .stButton > button[key^="del_"] {
        border: none !important;
        background: transparent !important;
        padding: 0px !important;
        margin: 0px !important;
        height: 24px !important;  /* Matches standard checkbox height */
        width: 24px !important;   /* Matches standard checkbox width */
        min-height: 24px !important;
        min-width: 24px !important;
        line-height: 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Remove the hover border to keep it sleek */
    .stButton > button[key^="del_"]:hover {
        background: rgba(255,255,255,0.1) !important;
        color: #ff4b4b !important;
    }

    .progress-wrapper {
        width: 100%; height: 100px; 
        display: flex; justify-content: center; align-items: center;
        margin-bottom: 10px;
    }
    .circular-chart { width: 80px; height: 80px; }
    .circle-bg { fill: none; stroke: #333; stroke-width: 2.8; }
    .circle { fill: none; stroke-width: 2.8; stroke-linecap: round; stroke: #76b372; }
    .percentage { fill: #76b372; font-family: sans-serif; font-size: 0.55em; text-anchor: middle; font-weight: bold; }
    
    /* Card Container Spacing */
    [data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

user = st.session_state.user_email
st.title("🗓️ Weekly Planner")
start_date = st.date_input("Week Starting", datetime.now().date() - timedelta(days=datetime.now().weekday()))
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- WEEKLY GRID ---
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total_tasks = len(tasks)
    done_tasks = sum(1 for t in tasks if t[2])
    progress_pct = int((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    with cols[i]:
        st.markdown(f"<div style='background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white;'><strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="progress-wrapper"><svg viewBox="0 0 36 36" class="circular-chart"><path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/><path class="circle" stroke-dasharray="{progress_pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/><text x="18" y="20.5" class="percentage">{progress_pct}%</text></svg></div>', unsafe_allow_html=True)
        
        # Add Input
        new_task = st.text_input("Add", key=f"in_{i}", label_visibility="collapsed", placeholder="+ Task")
        if st.button("ADD", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", (user, i, new_task, start_date, False))
                st.rerun()

        st.markdown("<hr style='margin:10px 0; border:0.5px solid #333;'>", unsafe_allow_html=True)
        
        # Task List
        for tid, tname, tdone in tasks:
            with st.container(border=True):
                c1, c2 = st.columns([0.25, 0.75])
                
                with c1:
                    if st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed"):
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (not tdone, tid))
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_{tid}"):
                        execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                        st.rerun()
                
                with c2:
                    text_style = "text-decoration: line-through; color: gray;" if tdone else "color: white;"
                    st.markdown(f"<p style='margin:0; font-size:12px; font-weight:bold; {text_style}'>{tname.upper()}</p>", unsafe_allow_html=True)

# --- CLEANUP ---
st.markdown("---")
if st.button("CLEAN FINISHED TASKS", use_container_width=True, type="primary"):
    execute_query("DELETE FROM weekly_planner WHERE user_email=%s AND week_start=%s AND is_done=True", (user, start_date))
    st.rerun()

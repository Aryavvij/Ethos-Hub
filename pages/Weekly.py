import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Weekly Planner", page_icon="🗓️")

# --- GATEKEEPER ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()

render_sidebar()

# --- CSS STYLING ---
st.markdown("""
    <style>
    /* Force the checkbox and label to align perfectly */
    [data-testid="stCheckbox"] {
        display: flex;
        align-items: center;
        padding: 5px 0;
    }
    
    [data-testid="stCheckbox"] > label {
        display: flex;
        align-items: center;
        margin-bottom: 0px !important; /* Remove Streamlit's default bottom margin */
        gap: 12px; /* Space between box and text */
    }

    /* Target the text inside the checkbox label */
    [data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding-top: 2px; /* Micro-adjustment for optical centering */
    }
    </style>
""", unsafe_allow_html=True)

for task in tasks:
    is_checked = st.checkbox(task.name.upper(), value=task.is_done, key=f"task_{task.id}")

# --- INITIALIZATION ---
user = st.session_state.user_email
start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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
    tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                        (user, i, start_date))
    
    total = len(tasks)
    done = sum(1 for t in tasks if t[2])
    pct = int((done / total * 100)) if total > 0 else 0
    
    with cols[i]:
        st.markdown(f"""
            <div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; width:100%; box-sizing:border-box;">
                <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" style="fill:#76b372; font-size:8px; text-anchor:middle; font-weight:bold;">{pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # --- TASK EXECUTION LIST (Clean: No Bin) ---
        for tid, tname, tdone in tasks:
            with st.container(border=True):
                t1, t2 = st.columns([0.2, 0.8])
                
                with t1:
                    if st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed"):
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (not tdone, tid))
                        st.rerun()
                
                with t2:
                    text_style = "text-decoration: line-through; color: gray;" if tdone else "color: white;"
                    st.markdown(f"<p style='margin:0; font-size:12px; font-weight:bold; {text_style}'>{tname.upper()}</p>", unsafe_allow_html=True)

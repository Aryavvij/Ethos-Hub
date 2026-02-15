import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar

st.set_page_config(layout="wide", page_title="Weekly Planner", page_icon="🗓️")

# --- INITIALIZATION ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()

render_sidebar()

user = st.session_state.user_email
start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- CSS STYLING: SYMMETRY & CENTERING ---
st.markdown("""
    <style>
    /* 1. Header & Chart Alignment */
    .day-header {
        background: #76b372; padding: 12px; border-radius: 8px; 
        text-align: center; color: white; margin-bottom: 10px; width: 100%;
    }
    .progress-wrapper {
        display: flex; justify-content: center; align-items: center;
        width: 100%; padding: 10px 0 20px 0;
    }
    .circular-chart { width: 85% !important; max-width: 90px; height: auto; }

    /* 2. THE TIGHT-WRAP TASK BOX */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        gap: 0rem !important;
    }

    /* 3. ROW CENTERING: Forces Tick + Text to Midline */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important; 
        justify-content: flex-start !important;
        padding: 8px 12px !important; /* Balanced internal breathing room */
        min-height: 48px;
    }

    .task-text {
        font-size: 13px !important; /* Scaled down for better fit */
        font-weight: 600 !important; 
        line-height: 1.1 !important;
        margin: 0 !important;
        padding-left: 10px !important; /* Space between tick and text */
        color: white;
        text-align: left;
        display: flex;
        align-items: center;
    }

    /* Checkbox Centering */
    div[data-testid="stCheckbox"] {
        margin: 0px !important;
        padding: 0px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    div[data-testid="stCheckbox"] label {
        margin-bottom: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Weekly Planner")

# --- 1. THE CENTRALIZED TASK ARCHITECT ---
with st.expander("🛠️ TASK ARCHITECT (Add / Edit / Delete)", expanded=False):
    c1, c2 = st.columns([1, 2])
    target_day = c1.selectbox("Select Day to Manage", days)
    day_idx = days.index(target_day)
    
    current_tasks = fetch_query("SELECT id, task_name FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", (user, day_idx, start_date))
    
    st.markdown("---")
    task_input = st.text_input("Add New Task", placeholder="E.g., FINISH PROJECT", key="add_input")
    if st.button("COMMIT NEW TASK", use_container_width=True, type="primary"):
        if task_input:
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, False)", (user, day_idx, task_input, start_date))
            st.rerun()

    if current_tasks:
        st.markdown("---")
        st.write(f"**Manage {target_day} Tasks**")
        for tid, tname in current_tasks:
            ec1, ec2, ec3 = st.columns([0.6, 0.2, 0.2])
            new_name = ec1.text_input("Label", value=tname, key=f"edit_{tid}", label_visibility="collapsed")
            if ec2.button("UPDATE", key=f"upd_{tid}", use_container_width=True):
                execute_query("UPDATE weekly_planner SET task_name=%s WHERE id=%s", (new_name, tid))
                st.rerun()
            if ec3.button("DEL", key=f"del_{tid}", use_container_width=True):
                execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                st.rerun()

# --- 2. THE 7-DAY GRID (TRACKING ONLY) ---
cols = st.columns(7, gap="small")

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    day_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", (user, i, start_date))
    
    total = len(day_tasks)
    done = sum(1 for t in day_tasks if t[2])
    pct = int((done / total * 100)) if total > 0 else 0
    
    with cols[i]:
        st.markdown(f'<div class="day-header"><strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime("%d %b")}</small></div>', unsafe_allow_html=True)
        
        # Circular Chart
        st.markdown(f'''<div class="progress-wrapper"><svg viewBox="0 0 36 36" class="circular-chart">
            <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <text x="18" y="20.5" style="fill:#76b372; font-size:10px; text-anchor:middle; font-weight:bold;">{pct}%</text></svg></div>''', unsafe_allow_html=True)
        
        for tid, tname, tdone in day_tasks:
            with st.container(border=True):
                t_c1, t_c2 = st.columns([0.25, 0.75], vertical_alignment="center")
                with t_c1:
                    new_val = st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed")
                    if new_val != tdone:
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (new_val, tid))
                        st.rerun()
                with t_c2:
                    text_decoration = "line-through" if tdone else "none"
                    text_color = "#666" if tdone else "white"
                    st.markdown(f'<div class="task-text" style="text-decoration: {text_decoration}; color: {text_color};">{tname.upper()}</div>', unsafe_allow_html=True)

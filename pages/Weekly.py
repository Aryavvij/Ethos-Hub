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
    .day-header {
        background: #76b372; padding: 12px; border-radius: 8px; 
        text-align: center; color: white; margin-bottom: 10px; width: 100%;
    }
    .day-header strong { font-size: 18px !important; display: block; }
    
    .progress-wrapper {
        display: flex; justify-content: center; align-items: center;
        width: 100%; padding: 10px 0 20px 0;
    }
    .circular-chart { width: 85% !important; max-width: 100px; height: auto; }
    .circle-bg { fill: none; stroke: #333; stroke-width: 3.5; }
    .circle { fill: none; stroke-width: 3.5; stroke: #76b372; stroke-linecap: round; }
    
    /* VERTICAL CENTERING & TIGHT BOXES */
    [data-testid="stVerticalBlock"] > div { padding-top: 0px !important; padding-bottom: 0px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding: 0px !important; margin-bottom: 5px !important; }

    .task-text {
        font-size: 13px !important; font-weight: 600 !important; 
        line-height: 1.1 !important; margin: 0 !important;
        display: flex !important; align-items: center !important; 
        min-height: 32px; width: 100%;
    }

    /* Action Buttons Styling - Minimalist emoji buttons */
    div[data-testid="column"] button {
        padding: 0px !important;
        border: none !important;
        background: transparent !important;
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
    
    if st.button("ADD TASK", use_container_width=True, type="primary"):
        if task_input:
            execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, False)", (user, day_idx, task_input, start_date))
            st.rerun()

# --- 7-DAY GRID ---
cols = st.columns(7, gap="small")

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    day_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", (user, i, start_date))
    
    total = len(day_tasks)
    done = sum(1 for t in day_tasks if t[2])
    pct = int((done / total * 100)) if total > 0 else 0
    
    with cols[i]:
        st.markdown(f'<div class="day-header"><strong>{day_name[:3].upper()}</strong><small>{this_date.strftime("%d %b")}</small></div>', unsafe_allow_html=True)
        
        st.markdown(f'''<div class="progress-wrapper"><svg viewBox="0 0 36 36" class="circular-chart">
            <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <text x="18" y="20.5" style="fill:#76b372; font-size:10px; text-anchor:middle; font-weight:bold;">{pct}%</text></svg></div>''', unsafe_allow_html=True)
        
        for tid, tname, tdone in day_tasks:
            with st.container(border=True):
                # Columns: Checkbox | Text | Edit | Delete
                t_c1, t_c2, t_c3, t_c4 = st.columns([0.15, 0.55, 0.15, 0.15], vertical_alignment="center")
                
                with t_c1:
                    new_val = st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed")
                    if new_val != tdone:
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (new_val, tid))
                        st.rerun()
                
                with t_c2:
                    text_decoration = "line-through" if tdone else "none"
                    text_color = "#666" if tdone else "white"
                    st.markdown(f'<div class="task-text" style="text-decoration: {text_decoration}; color: {text_color};">{tname.upper()}</div>', unsafe_allow_html=True)
                
                with t_c3:
                    if st.button(key=f"ed_{tid}"):
                        st.session_state[f"editing_{tid}"] = True
                        st.rerun()
                
                with t_c4:
                    if st.button(key=f"del_{tid}"):
                        execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                        st.rerun()

            # Inline Editor
            if st.session_state.get(f"editing_{tid}", False):
                with st.container(border=True):
                    new_name = st.text_input("Rename Task", value=tname, key=f"input_{tid}")
                    es1, es2 = st.columns(2)
                    if es1.button("SAVE", key=f"sv_{tid}", use_container_width=True):
                        execute_query("UPDATE weekly_planner SET task_name=%s WHERE id=%s", (new_name, tid))
                        st.session_state[f"editing_{tid}"] = False
                        st.rerun()
                    if es2.button("CANCEL", key=f"cn_{tid}", use_container_width=True):
                        st.session_state[f"editing_{tid}"] = False
                        st.rerun()

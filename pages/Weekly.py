import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar, ethos_observe # Import the decorator

st.set_page_config(layout="wide", page_title="Weekly Planner", page_icon="🗓️")

# --- 1. WRAPPED IN OBSERVER ---
@ethos_observe("Weekly Planner")
def show_weekly_page():
    # --- AUTH GATE ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.switch_page("Home.py")
        st.stop()

    render_sidebar()

    user = st.session_state.user_email
    start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # --- CSS STYLING ---
    st.markdown("""
        <style>
        .day-header { background: #76b372; padding: 12px; border-radius: 8px; text-align: center; color: white; margin-bottom: 10px; width: 100%; }
        .progress-wrapper { display: flex; justify-content: center; align-items: center; width: 100%; padding: 10px 0 20px 0; }
        .circular-chart { width: 85% !important; max-width: 90px; height: auto; }
        [data-testid="column"] { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: flex-start !important; padding: 8px 12px !important; min-height: 48px; }
        .task-text { font-size: 13px !important; font-weight: 600 !important; color: white; padding-left: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🗓️ Weekly Planner")

    # --- 2. THE CENTRALIZED TASK ARCHITECT ---
    with st.expander("TASK ARCHITECT", expanded=False):
        c1, c2 = st.columns([1, 2])
        target_day = c1.selectbox("Select Day to Manage", days)
        day_idx = days.index(target_day)
        current_tasks = fetch_query("SELECT id, task_name FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", (user, day_idx, start_date))
        
        st.markdown("---")
        task_input = st.text_input("Add New Task", key="add_input")
        if st.button("COMMIT NEW TASK", use_container_width=True, type="primary"):
            if task_input:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, False)", (user, day_idx, task_input, start_date))
                st.rerun()

    # --- 3. THE 7-DAY GRID ---
    cols = st.columns(7, gap="small")
    for i, day_name in enumerate(days):
        this_date = start_date + timedelta(days=i)
        day_tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", (user, i, start_date))
        
        total = len(day_tasks)
        done = sum(1 for t in day_tasks if t[2])
        pct = int((done / total * 100)) if total > 0 else 0
        
        with cols[i]:
            st.markdown(f'<div class="day-header"><strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime("%d %b")}</small></div>', unsafe_allow_html=True)
            
            # Progress Circle
            st.markdown(f'''<div class="progress-wrapper"><svg viewBox="0 0 36 36" class="circular-chart">
                <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                <path class="circle" stroke-dasharray="{pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                <text x="18" y="20.5" style="fill:#76b372; font-size:10px; text-anchor:middle; font-weight:bold;">{pct}%</text></svg></div>''', unsafe_allow_html=True)
            
            for tid, tname, tdone in day_tasks:
                with st.container(border=True):
                    t_c1, t_c2 = st.columns([0.25, 0.75], vertical_alignment="center")
                    with t_c1:
                        if st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed"):
                            if not tdone:
                                execute_query("UPDATE weekly_planner SET is_done=True WHERE id=%s", (tid,))
                                st.rerun()
                        elif tdone:
                            execute_query("UPDATE weekly_planner SET is_done=False WHERE id=%s", (tid,))
                            st.rerun()
                    with t_c2:
                        st.markdown(f'<div class="task-text">{tname.upper()}</div>', unsafe_allow_html=True)

# --- EXECUTE ---
show_weekly_page()

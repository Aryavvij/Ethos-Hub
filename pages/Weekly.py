import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

# --- CLEAN CSS: NO OVERLAP, JUST SPACING ---
st.markdown("""
    <style>
    /* Ensure all elements in the column are centered and spaced properly */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }
    
    /* Progress Circle: Fixed height prevents overlap with input boxes */
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

    /* Fix checkbox alignment within the task row */
    div[data-testid="stCheckbox"] {
        margin-bottom: 15px;
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

# 3. WEEKLY GRID (7 Columns)
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
        
        # PROGRESS RING (Fixed space wrapper)
        st.markdown(f"""
            <div class="progress-wrapper">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="{progress_pct}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.5" class="percentage">{progress_pct}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)
        
        # INPUT SECTION: Structured two-column table style
        with st.container():
            in_col, add_col = st.columns([0.65, 0.35], vertical_alignment="bottom")
            new_task = in_col.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New")
            if add_col.button("ADD", key=f"btn_{i}", use_container_width=True):
                if new_task:
                    execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                                  (user, i, new_task, start_date, False))
                    st.rerun()

        st.markdown("<hr style='margin:10px 0; border:0.5px solid #333;'>", unsafe_allow_html=True)
        
        # --- THE TASK TABLE ROWS ---
        for tid, tname, tdone in tasks:
            # 75:25 Split for Task Text and Checkbox
            row_col_text, row_col_check = st.columns([0.75, 0.25], vertical_alignment="center")
            
            with row_col_text:
                status_color = "#76b372" if tdone else "#ff4b4b"
                bg_opacity = "rgba(118, 179, 114, 0.15)" if tdone else "rgba(255, 75, 75, 0.05)"
                st.markdown(f"""
                    <div style="background:{bg_opacity}; color:{status_color}; border: 1px solid {status_color}; 
                    border-radius: 4px; text-align: left; font-size: 10px; height: 35px; 
                    line-height: 33px; padding: 0 8px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            
            with row_col_check:
                if st.checkbox("", value=tdone, key=f"chk_{tid}", label_visibility="collapsed"):
                    if not tdone:
                        execute_query("UPDATE weekly_planner SET is_done=True WHERE id=%s", (tid,))
                        st.rerun()
                else:
                    if tdone:
                        execute_query("UPDATE weekly_planner SET is_done=False WHERE id=%s", (tid,))
                        st.rerun()

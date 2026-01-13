import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

# --- GLOBAL SIDEBAR ---
with st.sidebar:
    st.success(f"Logged in: {st.session_state.user_email}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()
    st.markdown("---")

st.set_page_config(layout="wide", page_title="Weekly Planner")

# Load CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("🗓️ Weekly Planner")

# --- DATE LOGIC ---
today = datetime.now().date()
default_monday = today - timedelta(days=today.weekday())

with st.container():
    c1, c2 = st.columns([1, 1])
    with c1:
        start_date = st.date_input("Week Starting On (Monday):", default_monday)
    with c2:
        st.markdown(f"""
            <div style="padding-top: 28px;">
                <div style="background-color: #1e2129; padding: 10px; border-radius: 5px; border: 1px solid #333; text-align: center;">
                    <p style="margin:0; color: gray; font-size: 16px;">Viewing: {start_date.strftime("%B %Y")}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

user = st.session_state.user_email

# --- WEEKLY GRID ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_day_date = start_date + timedelta(days=i)
    
    with cols[i]:
        # Header Styling
        st.markdown(f"""
            <div style="background-color: #76b372; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                <p style="margin:0; font-weight:bold; color:white;">{day_name[:3].upper()}</p>
                <p style="margin:0; font-size:12px; color:white;">{this_day_date.strftime('%d %b')}</p>
            </div>
        """, unsafe_allow_html=True)

        # Task Input
        new_task = st.text_input("Add task", key=f"in_{i}", placeholder="+ Task", label_visibility="collapsed")
        if st.button("Add", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query(
                    "INSERT INTO weekly_planner (user_email, day_index, task_name, week_start) VALUES (%s, %s, %s, %s)",
                    (user, i, new_task, start_date)
                )
                st.rerun()
        
        st.markdown('<div style="height: 300px; overflow-y: auto;">', unsafe_allow_html=True)
        
        db_tasks = fetch_query(
            "SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", 
            (user, i, start_date)
        )
        
        done_count = 0
        if db_tasks:
            for tid, tname, tdone in db_tasks:
                # ALIGNMENT FIX: Tight ratio [0.9, 0.1] prevents text boxes from stretching
                t_col, d_col = st.columns([0.9, 0.1])
                
                with t_col:
                    is_checked = st.checkbox(tname, value=bool(tdone), key=f"chk_{tid}")
                    if is_checked != bool(tdone):
                        execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (is_checked, tid))
                        st.rerun()
                    if is_checked: done_count += 1
                
                with d_col:
                    # Small delete button
                    if st.button("×", key=f"del_{tid}", help="Delete"):
                        execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Summary Stats
        total_tasks = len(db_tasks)
        not_done = total_tasks - done_count
        st.markdown(f"""
            <div style="margin-top: 10px; border-top: 1px solid #444; padding-top: 10px;">
                <p style="color: #76b372; margin: 0; font-size: 13px;">✅ {done_count} | ⭕ {not_done}</p>
            </div>
        """, unsafe_allow_html=True)

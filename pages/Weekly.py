import streamlit as st
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. SET WIDE MODE & PAGE CONFIG
st.set_page_config(layout="wide", page_title="🗓️ Weekly Planner")

# --- CSS HEIGHT & SYMMETRY LOCK ---
# This ensures buttons and text boxes are identical in size and perfectly centered
st.markdown("""
    <style>
    /* Centers all items vertically in the column */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    /* Reduces the horizontal gap between the 3 boxes */
    div[data-testid="stHorizontalBlock"] {
        gap: 4px !important;
    }
    /* Lock Button Height to exactly 35px to match the text box */
    .stButton > button {
        height: 35px !important;
        min-height: 35px !important;
        max-height: 35px !important;
        padding: 0px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px !important;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

# SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Weekly Planner")

# Date Input (Auto-calculated to the current Monday)
start_date = st.date_input("Week Starting (Monday)", datetime.now().date() - timedelta(days=datetime.now().weekday()))

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# 3. WEEKLY GRID (7 Columns for 7 Days)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day_name in enumerate(days):
    this_date = start_date + timedelta(days=i)
    with cols[i]:
        # Day Header
        st.markdown(f"""<div style="background:#76b372; padding:8px; border-radius:5px; text-align:center; color:white; margin-bottom: 10px; width:100%;">
            <strong>{day_name[:3].upper()}</strong><br><small>{this_date.strftime('%d %b')}</small></div>""", unsafe_allow_html=True)
        
        # New Task Input
        new_task = st.text_input("Task", key=f"in_{i}", label_visibility="collapsed", placeholder="+ New Task")
        if st.button("Add Task", key=f"btn_{i}", use_container_width=True):
            if new_task:
                execute_query("INSERT INTO weekly_planner (user_email, day_index, task_name, week_start, is_done) VALUES (%s, %s, %s, %s, %s)", 
                              (user, i, new_task, start_date, False))
                st.rerun()
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        # Pull tasks from database
        tasks = fetch_query("SELECT id, task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s ORDER BY id ASC", 
                            (user, i, start_date))
        
        # --- TASK LIST RENDERING: IDENTICAL TRIPLE BLOCKS ---
        for tid, tname, tdone in tasks:
            # 1:3:1 Split ratio (0.2, 0.6, 0.2)
            c1, c2, c3 = st.columns([0.2, 0.6, 0.2])
            
            with c1:
                # Tick Button (Height 35px via CSS)
                if st.button("✔", key=f"done_{tid}", use_container_width=True):
                    execute_query("UPDATE weekly_planner SET is_done=%s WHERE id=%s", (not tdone, tid))
                    st.rerun()
            
            with c2:
                status_color = "#76b372" if tdone else "#ff4b4b"
                bg_opacity = "rgba(118, 179, 114, 0.2)" if tdone else "rgba(255, 75, 75, 0.1)"
                
                # Custom Markdown Box (Height matched exactly to 35px)
                st.markdown(f"""
                    <div style="background:{bg_opacity}; color:{status_color}; border: 1px solid {status_color}; 
                    border-radius: 4px; text-align: center; font-weight: bold; font-size: 10px; 
                    height: 35px; line-height: 33px; width: 100%; white-space: nowrap; 
                    overflow: hidden; text-overflow: ellipsis; box-sizing: border-box;">
                        {tname.upper()}
                    </div>
                """, unsafe_allow_html=True)
            
            with c3:
                # Cross Button (Height 35px via CSS)
                if st.button("✖", key=f"del_{tid}", use_container_width=True):
                    execute_query("DELETE FROM weekly_planner WHERE id=%s", (tid,))
                    st.rerun()

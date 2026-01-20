import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Monthly Events")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied.")
    st.stop()

render_sidebar()

# --- INITIALIZATION & FILTERS ---
user = st.session_state.user_email
st.title("Monthly Events")
today = datetime.now()

c1, c2 = st.columns([2, 1])
with c1:
    month_names = list(calendar.month_name)[1:] 
    selected_month_name = st.selectbox("Month", month_names, index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028], index=1)

month_num = list(calendar.month_name).index(selected_month_name)

# --- EVENT CREATION ---
with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event", use_container_width=True):
        if e_desc:
            execute_query("INSERT INTO events (user_email, event_date, description, is_done) VALUES (%s, %s, %s, %s)", 
                          (user, e_date, e_desc, False))
            st.rerun()

# --- CALENDAR STYLING ---
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 10px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- CALENDAR GRID GENERATION ---
cal_matrix = calendar.monthcalendar(year, month_num)
for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                cur_date = f"{year}-{month_num:02d}-{day:02d}"
                events = fetch_query("SELECT description, is_done FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                
                content = f'<p style="margin:0 0 5px 0; font-weight:bold; font-size:14px; color:#aaa;">{day}</p>'
                
                for desc, is_done in events:
                    bg = "rgba(118, 179, 114, 0.2)" if is_done else "rgba(255, 75, 75, 0.2)"
                    txt_c = "#76b372" if is_done else "#ff4b4b"
                    
                    content += f"""
                        <div style="font-size:10px; color:{txt_c}; background:{bg}; 
                        padding:3px 6px; border-radius:3px; margin-bottom:4px; 
                        border-left:3px solid {txt_c}; white-space: nowrap; 
                        overflow: hidden; text-overflow: ellipsis; font-weight: bold;">
                            {desc.upper()}
                        </div>
                    """
                
                st.markdown(f"""
                    <div style="height: 120px; border: 1px solid #333; border-radius: 8px; 
                    padding: 8px; background: rgba(255,255,255,0.02); overflow: hidden; margin-bottom: 10px;">
                        {content}
                    </div>
                """, unsafe_allow_html=True)

import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

st.set_page_config(layout="wide", page_title="Monthly Events")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied.")
    st.stop()

user = st.session_state.user_email

st.title("🗓️ Monthly Events")
today = datetime.now()

c1, c2 = st.columns([2, 1])
with c1:
    month_names = list(calendar.month_name)[1:] 
    selected_month_name = st.selectbox("Month", month_names, index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028], index=1)

month_num = list(calendar.month_name).index(selected_month_name)

with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event", use_container_width=True):
        if e_desc:
            execute_query("INSERT INTO events (user_email, event_date, description, is_done) VALUES (%s, %s, %s, %s)", 
                          (user, e_date, e_desc, False))
            st.rerun()

# --- 6. CALENDAR GRID (FIXED BOX SYMMETRY) ---
st.markdown("---")
cal_matrix = calendar.monthcalendar(year, month_num)
day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
header_cols = st.columns(7)

for i, d in enumerate(day_headers):
    header_cols[i].markdown(f"<p style='text-align:center; color:#76b372; font-weight:bold; font-size:16px; margin-bottom:0px;'>{d}</p>", unsafe_allow_html=True)

# --- 6. CALENDAR GRID (BOX-INTERNAL EVENTS) ---
for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                # THE FIX: One single div for everything. Event is forced INSIDE.
                cur_date = f"{year}-{month_num:02d}-{day:02d}"
                events = fetch_query("SELECT description, is_done FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                
                content = f'<p style="margin:0; font-weight:bold; font-size:14px; color:#aaa;">{day}</p>'
                for desc, is_done in events:
                    txt_c = "#76b372" if is_done else "#ff4b4b"
                    content += f"""
                        <div style="font-size:10px; color:{txt_c}; background:rgba(0,0,0,0.2); 
                        padding:2px 5px; border-radius:3px; margin-top:4px; border-left:2px solid {txt_c};
                        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            {desc.upper()}
                        </div>
                    """
                
                st.markdown(f"""
                    <div style="height: 120px; border: 1px solid #333; border-radius: 8px; padding: 8px; background: rgba(255,255,255,0.02); overflow-y: auto;">
                        {content}
                    </div>
                """, unsafe_allow_html=True)

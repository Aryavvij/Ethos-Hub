import streamlit as st
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# 1. FIT TO SCREEN
st.set_page_config(layout="wide", page_title="Monthly Events")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

# 3. SIDEBAR LOGOUT
with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("🗓️ Monthly Events")
today = datetime.now()

# 4. MONTH NAME SELECTORS
c1, c2 = st.columns([2, 1])
with c1:
    month_names = list(calendar.month_name)[1:] 
    selected_month_name = st.selectbox("Month", month_names, index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028], index=1)

month_num = list(calendar.month_name).index(selected_month_name)

# 5. ADD EVENT
with st.expander("➕ Add New Event"):
    e_date = st.date_input("Date", datetime(year, month_num, 1))
    e_desc = st.text_input("Event Name")
    if st.button("Save Event", use_container_width=True):
        if e_desc:
            execute_query("INSERT INTO events (user_email, event_date, description, is_done) VALUES (%s, %s, %s, %s)", 
                          (user, e_date, e_desc, False))
            st.rerun()

# --- 6. CALENDAR GRID ---
st.markdown("---")
cal_matrix = calendar.monthcalendar(year, month_num)
day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
header_cols = st.columns(7)

for i, d in enumerate(day_headers):
    header_cols[i].markdown(f"<p style='text-align:center; color:#76b372; font-weight:bold; font-size:18px; margin-bottom:0px;'>{d}</p>", unsafe_allow_html=True)

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            with cols[i]:
                # FIX: Fixed height outer div (150px) ensures the grid never shifts or grows
                st.markdown('<div style="height: 150px; border: 1px solid #333; border-radius: 10px; padding: 10px; background: rgba(255,255,255,0.02); overflow: hidden;">', unsafe_allow_html=True)
                st.markdown(f"<strong>{day}</strong>", unsafe_allow_html=True)
                
                # FIX: Internal scrollable area for events (100px)
                st.markdown('<div style="height: 100px; overflow-y: auto; overflow-x: hidden; padding-right: 2px;">', unsafe_allow_html=True)
                
                cur_date = f"{year}-{month_num:02d}-{day:02d}"
                events = fetch_query("SELECT id, description, is_done FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                
                for eid, desc, is_done in events:
                    # FIX: Ratios [0.15, 0.7, 0.15] ensure buttons are centered and same size
                    ec1, ec2, ec3 = st.columns([0.15, 0.7, 0.15])
                    
                    with ec1:
                        if st.button("✔", key=f"done_{eid}", use_container_width=True):
                            execute_query("UPDATE events SET is_done=True WHERE id=%s", (eid,))
                            st.rerun()
                    
                    with ec2:
                        bg = "rgba(118, 179, 114, 0.2)" if is_done else "rgba(255, 75, 75, 0.1)"
                        txt_c = "#76b372" if is_done else "#ff4b4b"
                        # FIX: Match height (34px) and line-height (32px) for perfect vertical centering
                        st.markdown(f"""<div style='background:{bg}; color:{txt_c}; border: 1px solid {txt_c};
                                     border-radius:4px; font-size:9px; font-weight: bold; text-align: center;
                                     height: 34px; line-height: 32px; white-space: nowrap; 
                                     overflow: hidden; text-overflow: ellipsis;'>
                                     {desc.upper()}</div>""", unsafe_allow_html=True)
                    
                    with ec3:
                        if st.button("✖", key=f"del_{eid}", use_container_width=True):
                            execute_query("DELETE FROM events WHERE id=%s", (eid,))
                            st.rerun()

                st.markdown('</div></div>', unsafe_allow_html=True)

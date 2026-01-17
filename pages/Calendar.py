import st as st
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
            execute_query("INSERT INTO events (user_email, event_date, description) VALUES (%s, %s, %s)", (user, e_date, e_desc))
            st.rerun()

# 6. CALENDAR GRID
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
                # FIXED HEIGHT CONTAINER to keep the grid symmetrical
                with st.container(border=True):
                    st.markdown(f"<p style='margin-bottom:5px;'><strong>{day}</strong></p>", unsafe_allow_html=True)
                    
                    # Scrollable area with FIXED HEIGHT to stop the box from growing
                    st.markdown('<div style="height:100px; overflow-y:auto; overflow-x:hidden;">', unsafe_allow_html=True)
                    
                    cur_date = f"{year}-{month_num:02d}-{day:02d}"
                    events = fetch_query("SELECT id, description FROM events WHERE user_email=%s AND event_date=%s", (user, cur_date))
                    
                    for eid, desc in events:
                        # Tight column ratio for text and delete button
                        ec1, ec2 = st.columns([0.82, 0.18])
                        with ec1:
                            # Stylish badge for the event
                            st.markdown(f"""<div style='background:rgba(118, 179, 114, 0.2); 
                                         color:#76b372; padding:2px 5px; border-radius:3px; 
                                         font-size:11px; margin-bottom:4px; border-left: 3px solid #76b372;
                                         white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
                                         {desc}</div>""", unsafe_allow_html=True)
                        with ec2:
                            # Small button that aligns with the badge height
                            if st.button("×", key=f"del_{eid}", help="Remove Event"):
                                execute_query("DELETE FROM events WHERE id=%s", (eid,))
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from database import fetch_query, execute_query
from datetime import datetime, time
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Weekly Timetable")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
st.title("📅 Weekly Timetable")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- TIME PICKER UTILITY ---
def time_picker(label_prefix, default_h=8, default_m=0, default_p="AM", key_suffix=""):
    st.write(f"**{label_prefix} Time**")
    p1, p2, p3 = st.columns([1, 1, 1])
    h = p1.selectbox(f"H{key_suffix}", [i for i in range(1, 13)], index=default_h-1, label_visibility="collapsed", key=f"h_{label_prefix}_{key_suffix}")
    m = p2.selectbox(f"M{key_suffix}", [f"{i:02d}" for i in range(60)], index=default_m, label_visibility="collapsed", key=f"m_{label_prefix}_{key_suffix}")
    period = p3.selectbox(f"P{key_suffix}", ["AM", "PM"], index=0 if default_p=="AM" else 1, label_visibility="collapsed", key=f"p_{label_prefix}_{key_suffix}")
    
    h24 = int(h)
    if period == "PM" and h24 != 12: h24 += 12
    if period == "AM" and h24 == 12: h24 = 0
    return time(h24, int(m))

# --- SCHEDULE MANAGER (ADD / EDIT / DELETE) ---
with st.expander("🛠️ Schedule Manager (Add, Edit, or Delete Activities)", expanded=False):
    mode = st.radio("Action Protocol", ["Add New", "Edit Activity", "Delete Activity"], horizontal=True)
    st.markdown("---")

    if mode == "Add New":
        r1c1, r1c2, r1c3 = st.columns([1, 2, 1])
        day_sel = r1c1.selectbox("Day", days, key="add_day")
        sub_sel = r1c2.text_input("Activity", placeholder="e.g. Data Structures Lab", key="add_sub")
        loc_sel = r1c3.text_input("Location", placeholder="e.g. AB5-201", key="add_loc")

        s_time = time_picker("Start", key_suffix="add_s")
        e_time = time_picker("End", default_h=9, key_suffix="add_e")

        if st.button("SAVE TO TIMETABLE", use_container_width=True, type="primary"):
            if sub_sel:
                time_range_str = f"{s_time.strftime('%H:%M')}-{e_time.strftime('%H:%M')}"
                execute_query("""
                    INSERT INTO timetable (user_email, day_name, start_time, subject, location) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user, day_sel, s_time, sub_sel, f"{time_range_str}|{loc_sel}"))
                st.rerun()
            else:
                st.error("Missing activity name.")

    else:
        all_activities = fetch_query("""
            SELECT id, day_name, subject, start_time 
            FROM timetable WHERE user_email=%s 
            ORDER BY CASE WHEN day_name='Monday' THEN 1 WHEN day_name='Tuesday' THEN 2 
            WHEN day_name='Wednesday' THEN 3 WHEN day_name='Thursday' THEN 4 
            WHEN day_name='Friday' THEN 5 WHEN day_name='Saturday' THEN 6 ELSE 7 END, start_time
        """, (user,))

        if all_activities:
            act_options = {f"{row[1]} | {row[2].upper()} ({row[3].strftime('%I:%M %p')})": row[0] for row in all_activities}
            selected_label = st.selectbox("Search & Select Activity to Modify", options=list(act_options.keys()))
            selected_id = act_options[selected_label]

            if mode == "Delete Activity":
                if st.button("CONFIRM PERMANENT DELETE", use_container_width=True, type="primary"):
                    execute_query("DELETE FROM timetable WHERE id=%s", (selected_id,))
                    st.success("Activity purged.")
                    st.rerun()
            
            elif mode == "Edit Activity":
                curr = fetch_query("SELECT day_name, subject, location, start_time FROM timetable WHERE id=%s", (selected_id,))[0]
                
                try:
                    curr_time_part, curr_loc = curr[2].split('|')
                    c_start_str, c_end_str = curr_time_part.split('-')
                    def_h = int(c_start_str.split(':')[0])
                    def_m = int(c_start_str.split(':')[1])
                except:
                    curr_loc = curr[2]
                    def_h, def_m = 8, 0

                e_r1c1, e_r1c2, e_r1c3 = st.columns([1, 2, 1])
                e_day = e_r1c1.selectbox("Update Day", days, index=days.index(curr[0]))
                e_sub = e_r1c2.text_input("Update Activity", value=curr[1])
                e_loc = e_r1c3.text_input("Update Location", value=curr_loc)

                e_start = time_picker("Update Start", default_h=def_h, default_m=def_m, key_suffix="edit_s")
                e_end = time_picker("Update End", key_suffix="edit_e")

                if st.button("PUSH UPDATES", use_container_width=True, type="primary"):
                    time_range_str = f"{e_start.strftime('%H:%M')}-{e_end.strftime('%H:%M')}"
                    execute_query("""
                        UPDATE timetable SET day_name=%s, subject=%s, location=%s, start_time=%s 
                        WHERE id=%s
                    """, (e_day, e_sub, f"{time_range_str}|{e_loc}", e_start, selected_id))
                    st.rerun()
        else:
            st.info("Your timetable is currently empty.")

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- WEEKLY GRID RENDERING ---
cols = st.columns(len(days))

for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"<h4 style='text-align: center; color: #76b372;'>{day[:3].upper()}</h4>", unsafe_allow_html=True)
        day_classes = fetch_query("""
            SELECT id, start_time, subject, location 
            FROM timetable 
            WHERE user_email=%s AND day_name=%s 
            ORDER BY start_time ASC
        """, (user, day))
        
        for cid, ctime, csub, cloc_raw in day_classes:
            with st.container(border=True):
                try:
                    time_part, loc = cloc_raw.split('|')
                    start_str, end_str = time_part.split('-')
                    display_start = datetime.strptime(start_str, "%H:%M").strftime("%I:%M %p")
                    display_end = datetime.strptime(end_str, "%H:%M").strftime("%I:%M %p")
                    display_time = f"{display_start} - {display_end}"
                except:
                    display_time = ctime.strftime('%I:%M %p')
                    loc = cloc_raw

                st.markdown(f"<span style='color:#76b372; font-weight:bold; font-size:12px;'>{display_time}</span>", unsafe_allow_html=True)
                st.markdown(f"**{csub.upper()}**")
                if loc:
                    st.caption(f"📍 {loc}")

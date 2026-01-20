import streamlit as st
from database import fetch_query, execute_query
from datetime import datetime, time
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Weekly Timetable")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page.")
    if st.button("Go to Home"): st.switch_page("Home.py")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
st.title("📅 Weekly Timetable")
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- CLASS SCHEDULER ENGINE ---
with st.expander("➕ Add Class to Schedule", expanded=False):
    r1c1, r1c2, r1c3 = st.columns([1, 2, 1])
    day_sel = r1c1.selectbox("Day", days)
    sub_sel = r1c2.text_input("Subject", placeholder="e.g. Data Structures")
    loc_sel = r1c3.text_input("Location", placeholder="e.g. AB5-201")

    def time_picker(label_prefix):
        st.write(f"**{label_prefix} Time**")
        p1, p2, p3 = st.columns([1, 1, 1])
        h = p1.selectbox(f"Hour ({label_prefix})", [i for i in range(1, 13)], index=8, label_visibility="collapsed")
        m = p2.selectbox(f"Minute ({label_prefix})", [f"{i:02d}" for i in range(60)], index=0, label_visibility="collapsed")
        period = p3.selectbox(f"AM/PM ({label_prefix})", ["AM", "PM"], index=0, label_visibility="collapsed")
        
        h24 = int(h)
        if period == "PM" and h24 != 12: h24 += 12
        if period == "AM" and h24 == 12: h24 = 0
        return time(h24, int(m))

    start_time_final = time_picker("Start")
    end_time_final = time_picker("End")

    if st.button("Save Class", use_container_width=True):
        if sub_sel:
            time_range_str = f"{start_time_final.strftime('%H:%M')}-{end_time_final.strftime('%H:%M')}"
            execute_query("""
                INSERT INTO timetable (user_email, day_name, start_time, subject, location) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user, day_sel, start_time_final, sub_sel, f"{time_range_str}|{loc_sel}"))
            st.rerun()
        else:
            st.error("Please enter a subject.")

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
                
                if st.button("Delete", key=f"class_{cid}", use_container_width=True):
                    execute_query("DELETE FROM timetable WHERE id=%s", (cid,))
                    st.rerun()

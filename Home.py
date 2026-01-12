import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from database import get_db_connection, execute_query, fetch_query

# --- 1. AUTHENTICATION UTILITIES ---

# hashing for security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(email, password):
    # check the cloud database for this user
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    result = fetch_query(query, (email, password))
    return result[0] if result else None

def signup_user(email, password):
    # add a new user to the cloud
    try:
        query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        execute_query(query, (email, password))
        return True
    except Exception as e:
        st.error(f"Sign up error: {e}")
        return False

# --- 2. AUTHENTICATION UI ---

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# show login screen if not authenticated
if not st.session_state.logged_in:
    st.title("Ethos System Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            result = login_user(email, make_hashes(password))
            if result:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun() 
            else:
                st.error("Incorrect Email or Password")
    
    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("New Email", key="signup_email")
        new_pass = st.text_input("New Password", type='password', key="signup_pass")
        confirm_pass = st.text_input("Confirm Password", type='password', key="signup_confirm")
        
        if st.button("Sign Up"):
            if new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_email and new_pass:
                hashed_new_pswd = make_hashes(new_pass)
                if signup_user(new_email, hashed_new_pswd):
                    st.success("Account created successfully!")
                    st.info("You can now go to the Login tab to enter your system.")
                else:
                    st.error("This email is already registered.")
            else:
                st.warning("Please fill in all fields.")
    
    # CRITICAL: This stops the script ONLY for unauthenticated users
    st.stop() 

# --- 3. ACTUAL HOME PAGE (Only reached if logged_in is True) ---

# Load styling - Note: styling usually applies better outside containers
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# Sidebar status and logout
st.sidebar.success(f"Logged in: {st.session_state.user_email}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown('<div class="home-container">', unsafe_allow_html=True)
st.title("ETHOS HUB")

# Top section for big picture goals
st.markdown("### Strategic Semester Goals")
g1, g2, g3 = st.columns(3)

with g1:
    with st.container(border=True):
        st.markdown('<p class="card-title">Academic</p>', unsafe_allow_html=True)
        st.text_area("A", value="• Target GPA: 4.0", height=150, label_visibility="collapsed", key="ac_goals")

with g2:
    with st.container(border=True):
        st.markdown('<p class="card-title">Health</p>', unsafe_allow_html=True)
        st.text_area("H", value="• Gym 4x Weekly", height=150, label_visibility="collapsed", key="he_goals")

with g3:
    with st.container(border=True):
        st.markdown('<p class="card-title">Others</p>', unsafe_allow_html=True)
        st.text_area("O", value="• Learn Python", height=150, label_visibility="collapsed", key="ot_goals")

st.markdown("---")

# --- 3. UPDATED SYSTEM STATUS SECTION ---
st.markdown("### Today's Focus")
w1, w2, w3 = st.columns(3)

# 1. Priorities (Weekly Tasks + Calendar Events)
with w1:
    with st.container(border=True):
        st.markdown('<p class="card-title">📋 Today\'s Priorities</p>', unsafe_allow_html=True)
        
        # Determine the current day index (Monday=0)
        today_date = datetime.now().date()
        day_idx = today_date.weekday()
        current_monday = today_date - timedelta(days=day_idx)
        
        # Pull Tasks from Weekly Planner
        tasks = fetch_query(
            "SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s",
            (st.session_state.user_email, day_idx, current_monday)
        )
        
        # Pull Events from Calendar
        events = fetch_query(
            "SELECT description FROM events WHERE user_email=%s AND event_date=%s",
            (st.session_state.user_email, today_date)
        )
        
        if not tasks and not events:
            st.markdown("<p style='color:gray; font-size:14px;'>Nothing scheduled for today.</p>", unsafe_allow_html=True)
        else:
            # Display Calendar Events first (as alerts)
            for ev in events:
                st.markdown(f"**📍 EVENT: {ev[0]}**")
            
            # Display Weekly Tasks
            for tname, tdone in tasks:
                status = "✅" if tdone else "⭕"
                st.markdown(f"<p style='font-size:14px;'>{status} {tname}</p>", unsafe_allow_html=True)

# 2. Budget Snapshot (Keep existing logic)
with w2:
    with st.container(border=True):
        st.markdown('<p class="card-title">💰 Budget Snapshot</p>', unsafe_allow_html=True)
        current_period = datetime.now().strftime("%B %Y")
        try:
            query = "SELECT SUM(CAST(plan AS REAL)), SUM(CAST(actual AS REAL)) FROM finances WHERE period = %s"
            result = fetch_query(query, (current_period,))
            if result and result[0][0] is not None:
                remaining = float(result[0][0]) - (float(result[0][1]) if result[0][1] else 0)
                color = "#76b372" if remaining >= 0 else "#ff4b4b"
                st.markdown(f"<p class='status-text-large' style='margin-top:20px;'>Remaining: <span style='color:{color}; font-weight:bold;'>Rs {remaining:,.2f}</span></p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:gray; font-size:12px;'>No data for {current_period}</p>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

# 3. Today's Classes (Replacing Inspiration)
with w3:
    with st.container(border=True):
        st.markdown('<p class="card-title">🎓 Today\'s Classes</p>', unsafe_allow_html=True)
        day_name = datetime.now().strftime("%A")
        
        # Fetch classes for the current day
        classes = fetch_query(
            "SELECT start_time, subject, location FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC",
            (st.session_state.user_email, day_name)
        )
        
        if classes:
            for ctime, csub, cloc in classes:
                # Format time to HH:MM
                time_str = ctime.strftime("%H:%M")
                st.markdown(f"""
                    <div style="border-left: 3px solid #76b372; padding-left: 10px; margin-bottom: 8px;">
                        <p style="margin:0; font-weight:bold; font-size:14px;">{time_str} - {csub}</p>
                        <p style="margin:0; font-size:12px; color:gray;">📍 {cloc if cloc else 'No Location'}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:gray; font-size:14px;'>No classes today. Rest up!</p>", unsafe_allow_html=True)

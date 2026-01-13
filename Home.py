import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timedelta  
from database import get_db_connection, execute_query, fetch_query

# Initialize session state keys at the very start
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# ... rest of your Home.py code ...

# --- 1. AUTHENTICATION UTILITIES ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(email, password):
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    result = fetch_query(query, (email, password))
    return result[0] if result else None

def signup_user(email, password):
    try:
        query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        execute_query(query, (email, password))
        return True
    except Exception as e:
        return False

# --- 2. AUTHENTICATION UI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Ethos System Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            try:
                result = login_user(email, make_hashes(password))
                if result:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Incorrect Email or Password")
            except Exception as e:
                st.error("Connection lost. Please wait 5 seconds and try again.")
    
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
                if signup_user(new_email, make_hashes(new_pass)):
                    st.success("Account created! Go to Login tab.")
                else:
                    st.error("Email already registered.")
    st.stop() 

# --- 3. ACTUAL HOME PAGE ---
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# Sidebar logout
st.sidebar.success(f"User: {st.session_state.user_email}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = None 
    st.rerun()

st.title("ETHOS HUB")
user = st.session_state.user_email

# --- STRATEGIC SEMESTER GOALS (Persistent Fix) ---
st.markdown("### 🎯 Strategic Semester Goals")
existing_goals = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = existing_goals[0] if existing_goals else ("", "", "")

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('<p class="card-title">Academic</p>', unsafe_allow_html=True)
        new_acad = st.text_area("A", value=g_acad, height=100, label_visibility="collapsed", key="ac_goals")
with g2:
    with st.container(border=True):
        st.markdown('<p class="card-title">Health</p>', unsafe_allow_html=True)
        new_health = st.text_area("H", value=g_health, height=100, label_visibility="collapsed", key="he_goals")
with g3:
    with st.container(border=True):
        st.markdown('<p class="card-title">Others</p>', unsafe_allow_html=True)
        new_pers = st.text_area("O", value=g_pers, height=100, label_visibility="collapsed", key="ot_goals")

if st.button("Update Goals"):
    execute_query("""
        INSERT INTO semester_goals (user_email, academic, health, personal)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_email) DO UPDATE SET 
        academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal
    """, (user, new_acad, new_health, new_pers))
    st.success("Goals updated!")

st.markdown("---")

# --- TODAY'S FOCUS SECTION ---
st.markdown("### Today's Focus")
w1, w2, w3 = st.columns(3)

# 1. Priorities (Tasks + Calendar)
with w1:
    with st.container(border=True):
        st.markdown('<p class="card-title">📋 Today\'s Priorities</p>', unsafe_allow_html=True)
        t_date = datetime.now().date()
        day_idx = t_date.weekday()
        current_monday = t_date - timedelta(days=day_idx)
        
        tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, day_idx, current_monday))
        events = fetch_query("SELECT description FROM events WHERE user_email=%s AND event_date=%s", (user, t_date))
        
        if not tasks and not events:
            st.caption("Nothing scheduled.")
        else:
            for ev in events: st.markdown(f"**📍 {ev[0]}**")
            for tname, tdone in tasks:
                st.markdown(f"{'✅' if tdone else '⭕'} {tname}")

# 2. Budget & Debt Snapshot
with w2:
    with st.container(border=True):
        st.markdown('<p class="card-title">💰 Financial Status</p>', unsafe_allow_html=True)
        
        # Get current month/year for filtering
        now = datetime.now()
        curr_month = now.month
        curr_year = now.year

        # 1. Calculate Remaining Budget for CURRENT MONTH ONLY
        # This ensures Jan data doesn't mix with Dec or Feb
        budget_query = """
            SELECT SUM(CAST(plan AS REAL) - CAST(actual AS REAL)) 
            FROM finances 
            WHERE user_email = %s 
            AND period = %s
        """
        current_period = now.strftime("%B %Y") # e.g., "January 2026"
        budget_res = fetch_query(budget_query, (user, current_period))
        rem_money = budget_res[0][0] if budget_res and budget_res[0][0] is not None else 0
        
        # 2. Calculate Total Debt (Usually all-time, but can be filtered if needed)
        debt_query = "SELECT SUM(amount) FROM debt WHERE user_email = %s"
        debt_res = fetch_query(debt_query, (user,))
        total_debt = debt_res[0][0] if debt_res and debt_res[0][0] is not None else 0
        
        st.markdown(f"""
            <div style="margin-top:10px;">
                <p style="margin:0; font-size:14px; color:gray;">{current_period} Budget:</p>
                <p style="margin:0; font-size:20px; color:#76b372; font-weight:bold;">Rs {rem_money:,.2f}</p>
                <hr style="margin:10px 0; border-color:#333;">
                <p style="margin:0; font-size:14px; color:gray;">Total Debt Owed:</p>
                <p style="margin:0; font-size:20px; color:#ff4b4b; font-weight:bold;">Rs {total_debt:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

# 3. Today's Classes
with w3:
    with st.container(border=True):
        st.markdown('<p class="card-title">🎓 Today\'s Classes</p>', unsafe_allow_html=True)
        day_name = datetime.now().strftime("%A")
        classes = fetch_query("SELECT start_time, subject, location FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC", (user, day_name))
        
        if classes:
            for ctime, csub, cloc in classes:
                st.markdown(f"**{ctime.strftime('%H:%M')}** - {csub} (📍{cloc})")
        else:
            st.caption("No classes today.")

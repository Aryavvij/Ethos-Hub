import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. DATABASE UTILITIES ---

# setup the user table if it's missing
def init_user_db():
    conn = sqlite3.connect('ethos.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

# hashing for security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# check credentials against the db
from database import get_db_connection, execute_query, fetch_query

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
    except Exception:
        return False

init_user_db()

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
    
    # stop here so the home page doesn't leak behind the login
    st.stop() 

# --- 3. ACTUAL HOME PAGE ---

# load styling
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# sidebar status and logout
st.sidebar.success(f"Logged in: {st.session_state.user_email}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown('<div class="home-container">', unsafe_allow_html=True)
st.title("ETHOS HUB")

# top section for big picture goals
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

# dashboard view of different system modules
st.markdown("### System Status")
w1, w2, w3 = st.columns(3)

with w1:
    with st.container(border=True):
        st.markdown('<p class="card-title">📋 Today\'s Priorities</p>', unsafe_allow_html=True)
        # pull tasks from the weekly planner session state
        day_idx = (datetime.now().weekday() + 1) % 7 
        if 'weekly_data' in st.session_state and st.session_state.weekly_data[day_idx]:
            for task in st.session_state.weekly_data[day_idx][:3]:
                st.markdown(f"<p class='status-text-large'>• {task['name']}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='status-text-large' style='color:gray;'>No tasks for today.</p>", unsafe_allow_html=True)

with w2:
    with st.container(border=True):
        st.markdown('<p class="card-title">💰 Budget Snapshot</p>', unsafe_allow_html=True)
        
        try:
            conn = sqlite3.connect('ethos.db')
            current_period = datetime.now().strftime("%B %Y") 
            
            # calculate remaining budget from the finance table
            query = """
                SELECT 
                    SUM(CAST(plan AS REAL)) as total_plan, 
                    SUM(CAST(actual AS REAL)) as total_actual 
                FROM finances 
                WHERE period = ?
            """
            df_budget = pd.read_sql_query(query, conn, params=(current_period,))
            conn.close()

            planned = df_budget['total_plan'].iloc[0] if not df_budget['total_plan'].isnull().all() else 0.0
            actual = df_budget['total_actual'].iloc[0] if not df_budget['total_actual'].isnull().all() else 0.0
            
            remaining = planned - actual
            color = "#76b372" if remaining >= 0 else "#ff4b4b"
            
            st.markdown(f"""
                <p class='status-text-large' style='margin-top:20px;'>
                    Remaining: <span style='color:{color}; font-weight:bold;'>Rs {remaining:,.2f}</span>
                </p>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f"<p style='color:gray; font-size:12px;'>Status: No data found for {current_period}</p>", unsafe_allow_html=True)

with w3:
    with st.container(border=True):
        st.markdown('<p class="card-title">💡 Daily Inspiration</p>', unsafe_allow_html=True)
        st.text_area("Q", value="Inspiration comes only during work", height=100, label_visibility="collapsed", key="quote_in")

st.markdown('</div>', unsafe_allow_html=True)

# --- DANGER ZONE (Bottom of Home Page) ---
st.markdown("---")
with st.expander("Reset Cloud Data"):
    st.write("This will permanently delete your data from the cloud tables. This cannot be undone.")
    
    # Confirmation text to prevent accidental clicks
    confirm_text = st.text_input("Type 'DELETE' to enable the reset button")
    
    col_reset1, col_reset2 = st.columns(2)
    
    with col_reset1:
        if st.button("Clear Weekly Planner", disabled=(confirm_text != "DELETE")):
            execute_query("DELETE FROM weekly_planner WHERE user_email = %s", (st.session_state.user_email,))
            st.success("Weekly tasks cleared.")
            
    with col_reset2:
        if st.button("Clear Habit History", disabled=(confirm_text != "DELETE")):
            execute_query("DELETE FROM habits WHERE user_email = %s", (st.session_state.user_email,))
            st.success("Habit data cleared.")
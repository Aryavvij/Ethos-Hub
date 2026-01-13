import streamlit as st
import hashlib
from datetime import datetime, timedelta  
from database import execute_query, fetch_query

# --- AUTH UTILS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.title("Ethos System Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            res = fetch_query("SELECT password FROM users WHERE email=%s", (email,))
            if res and res[0][0] == make_hashes(password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun() 
            else:
                st.error("Incorrect Email or Password")
    
    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("New Email", key="signup_email")
        new_pass = st.text_input("New Password", type='password', key="signup_pass")
        if st.button("Sign Up"):
            hashed_pass = make_hashes(new_pass)
            try:
                execute_query("INSERT INTO users (email, password) VALUES (%s, %s)", (new_email, hashed_pass))
                st.success("Account created! Go to Login tab.")
            except:
                st.error("Email already exists.")
    st.stop() 

# --- HOME DASHBOARD ---
user = st.session_state.user_email
st.sidebar.success(f"User: {user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("ETHOS HUB")

# 1. STRATEGIC SEMESTER GOALS
st.markdown("### 🎯 Strategic Semester Goals")
res = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = res[0] if res else ("", "", "")

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold;">Academic</p>', unsafe_allow_html=True)
        new_acad = st.text_area("A", value=g_acad, height=100, label_visibility="collapsed", key="ac")
with g2:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold;">Health</p>', unsafe_allow_html=True)
        new_health = st.text_area("H", value=g_health, height=100, label_visibility="collapsed", key="he")
with g3:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold;">Others</p>', unsafe_allow_html=True)
        new_pers = st.text_area("O", value=g_pers, height=100, label_visibility="collapsed", key="ot")

if st.button("Update Goals"):
    execute_query("INSERT INTO semester_goals (user_email, academic, health, personal) VALUES (%s,%s,%s,%s) ON CONFLICT (user_email) DO UPDATE SET academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal", (user, new_acad, new_health, new_pers))
    st.success("Goals updated!")

st.markdown("---")

# 2. TODAY'S FOCUS SECTION
st.markdown("### Today's Focus")
w1, w2, w3 = st.columns(3)

with w1:
    with st.container(border=True):
        st.markdown('**📋 Today\'s Priorities**')
        t_date = datetime.now().date()
        tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, t_date.weekday(), t_date - timedelta(days=t_date.weekday())))
        for tname, tdone in tasks:
            st.markdown(f"{'✅' if tdone else '⭕'} {tname}")

# --- Inside Home.py Focus Section ---
with w2:
    with st.container(border=True):
        st.markdown('**💰 Financial Status**')
        period = datetime.now().strftime("%B %Y") # January 2026
        
        # 1. REMAINING BUDGET CALCULATION
        # Logic: (Total Planned) - (Total Actual) for the month
        budget_res = fetch_query("""
            SELECT SUM(CAST(plan AS REAL)) - SUM(CAST(actual AS REAL)) 
            FROM finances 
            WHERE user_email=%s AND period=%s
        """, (user, period))
        
        # 2. TOTAL DEBT CALCULATION
        debt_res = fetch_query("SELECT SUM(CAST(amount AS REAL)) FROM debt WHERE user_email=%s", (user,))
        
        rem_val = budget_res[0][0] if budget_res and budget_res[0][0] is not None else 0
        debt_val = debt_res[0][0] if debt_res and debt_res[0][0] is not None else 0
        
        st.markdown(f"""
            <div style="margin-top:10px;">
                <p style="margin:0; font-size:14px; color:gray;">Remaining ({period}):</p>
                <p style="margin:0; font-size:22px; color:#76b372; font-weight:bold;">Rs {rem_val:,.2f}</p>
                <hr style="margin:10px 0; border-color:#333;">
                <p style="margin:0; font-size:14px; color:gray;">Total Debt Owed:</p>
                <p style="margin:0; font-size:22px; color:#ff4b4b; font-weight:bold;">Rs {debt_val:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

with w3:
    with st.container(border=True):
        st.markdown('**🎓 Today\'s Classes**')
        classes = fetch_query("SELECT start_time, subject FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC", (user, datetime.now().strftime("%A")))
        for ctime, csub in classes:
            st.markdown(f"**{ctime.strftime('%H:%M')}** - {csub}")

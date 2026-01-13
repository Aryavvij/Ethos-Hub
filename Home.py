import streamlit as st
import hashlib
from datetime import datetime, timedelta
from database import execute_query, fetch_query

# 1. INITIALIZE SESSION STATE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- AUTH UI ---
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
                st.error("Invalid credentials")
    st.stop()

# --- ACTUAL HOME PAGE ---
user = st.session_state.user_email
st.sidebar.success(f"User: {user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.rerun()

st.title("ETHOS HUB")

# STRATEGIC GOALS
st.markdown("### 🎯 Semester Goals")
res = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = res[0] if res else ("", "", "")

g1, g2, g3 = st.columns(3)
new_acad = g1.text_area("Academic", value=g_acad, height=100)
new_health = g2.text_area("Health", value=g_health, height=100)
new_pers = g3.text_area("Personal", value=g_pers, height=100)

if st.button("Update Goals"):
    execute_query("""
        INSERT INTO semester_goals (user_email, academic, health, personal)
        VALUES (%s, %s, %s, %s) ON CONFLICT (user_email) 
        DO UPDATE SET academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal
    """, (user, new_acad, new_health, new_pers))
    st.success("Goals Saved")

# FINANCIAL SNAPSHOT (Jan Filter Fix)
st.markdown("---")
w1, w2, w3 = st.columns(3)
with w2:
    with st.container(border=True):
        st.markdown("**💰 Financial Status**")
        now = datetime.now()
        period = now.strftime("%B %Y")
        budget_res = fetch_query("SELECT SUM(CAST(plan AS REAL) - CAST(actual AS REAL)) FROM finances WHERE user_email=%s AND period=%s", (user, period))
        debt_res = fetch_query("SELECT SUM(amount) FROM debt WHERE user_email=%s", (user,))
        
        rem = budget_res[0][0] or 0
        debt = debt_res[0][0] or 0
        st.write(f"Remaining ({period}): Rs {rem:,.2f}")
        st.write(f"Total Debt: Rs {debt:,.2f}")

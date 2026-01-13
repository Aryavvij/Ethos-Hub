import streamlit as st
import hashlib
from datetime import datetime, timedelta  
from database import execute_query, fetch_query

# --- AUTH UTILS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Ethos System Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            res = fetch_query("SELECT * FROM users WHERE email=%s AND password=%s", (email, make_hashes(password)))
            if res:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid credentials")
    # ... (Sign up tab code here) ...
    st.stop()

# --- THE FULL DASHBOARD ---
user = st.session_state.user_email
st.sidebar.success(f"User: {user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("ETHOS HUB")

# SEMESTER GOALS CARDS
st.markdown("### 🎯 Strategic Semester Goals")
res = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = res[0] if res else ("", "", "")

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('<p style="font-weight:bold; color:#76b372;">Academic</p>', unsafe_allow_html=True)
        new_acad = st.text_area("A", value=g_acad, height=100, label_visibility="collapsed", key="ac")
with g2:
    with st.container(border=True):
        st.markdown('<p style="font-weight:bold; color:#76b372;">Health</p>', unsafe_allow_html=True)
        new_health = st.text_area("H", value=g_health, height=100, label_visibility="collapsed", key="he")
with g3:
    with st.container(border=True):
        st.markdown('<p style="font-weight:bold; color:#76b372;">Others</p>', unsafe_allow_html=True)
        new_pers = st.text_area("O", value=g_pers, height=100, label_visibility="collapsed", key="ot")

if st.button("Update Goals"):
    execute_query("INSERT INTO semester_goals (user_email, academic, health, personal) VALUES (%s,%s,%s,%s) ON CONFLICT (user_email) DO UPDATE SET academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal", (user, new_acad, new_health, new_pers))
    st.success("Goals Saved")

st.markdown("---")

# TODAY'S FOCUS SECTION
st.markdown("### Today's Focus")
w1, w2, w3 = st.columns(3)

with w1:
    with st.container(border=True):
        st.markdown("**📋 Today's Priorities**")
        # Pulling from Weekly and Events...
        # (Insert your full Priorities logic here)

with w2:
    with st.container(border=True):
        st.markdown("**💰 Financial Status**")
        # (Insert your Budget/Debt snapshot logic here)

with w3:
    with st.container(border=True):
        st.markdown("**🎓 Today's Classes**")
        # (Insert your Timetable logic here)

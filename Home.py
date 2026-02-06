import streamlit as st
import hashlib
from datetime import datetime, timedelta  
from database import execute_query, fetch_query
from utils import render_sidebar
from streamlit_cookies_controller import CookieController

st.set_page_config(layout="wide", page_title="Ethos Hub")

controller = CookieController()
cookie_name = "ethos_user_token"

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- STICKY LOGIN LOGIC (WITH SAFETY PATCH) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    try:
        all_cookies = controller.get_all()
        if all_cookies and cookie_name in all_cookies:
            saved_user = controller.get(cookie_name)
            if saved_user:
                st.session_state.logged_in = True
                st.session_state.user_email = saved_user
    except Exception:
        pass

# --- AUTHENTICATION SECTION ---
if not st.session_state.logged_in:
    st.title("🛡️ Ethos System Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login", use_container_width=True):
            res = fetch_query("SELECT password FROM users WHERE email=%s", (email,))
            if res and res[0][0] == make_hashes(password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                
                controller.set(cookie_name, email)
                st.rerun() 
            else:
                st.error("Incorrect Email or Password")
    
    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("New Email", key="signup_email")
        new_pass = st.text_input("New Password", type='password', key="signup_pass")
        if st.button("Sign Up", use_container_width=True):
            hashed_pass = make_hashes(new_pass)
            try:
                execute_query("INSERT INTO users (email, password) VALUES (%s, %s)", (new_email, hashed_pass))
                st.success("Account created! Go to Login tab.")
            except:
                st.error("Email already exists.")
    st.stop() 

# --- DASHBOARD INITIALIZATION ---
user = st.session_state.user_email
render_sidebar()

st.title("ETHOS HUB")

# --- STRATEGIC SEMESTER GOALS ---
st.markdown("### Strategic Personal Goals")
res = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = res[0] if res else ("", "", "")

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Academic</p>', unsafe_allow_html=True)
        new_acad = st.text_area("A", value=g_acad, height=100, label_visibility="collapsed", key="ac")
with g2:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Health</p>', unsafe_allow_html=True)
        new_health = st.text_area("H", value=g_health, height=100, label_visibility="collapsed", key="he")
with g3:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Others</p>', unsafe_allow_html=True)
        new_pers = st.text_area("O", value=g_pers, height=100, label_visibility="collapsed", key="ot")

if st.button("Update Goals", use_container_width=True):
    execute_query("""
        INSERT INTO semester_goals (user_email, academic, health, personal) 
        VALUES (%s,%s,%s,%s) 
        ON CONFLICT (user_email) 
        DO UPDATE SET academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal
    """, (user, new_acad, new_health, new_pers))
    st.success("Goals updated!")

st.markdown("---")

# --- DAILY BRIEFING CENTER ---
st.markdown("### Today's Briefing")

t_date = datetime.now().date()
d_idx = t_date.weekday()
w_start = t_date - timedelta(days=d_idx)

b1, b2, b3 = st.columns(3)
label_style = "margin:0; font-size:13px; color:gray; line-height:1.2; font-weight:500; text-transform:uppercase; letter-spacing:0.5px;"

with b1:
    with st.container(border=True):
        st.markdown(f"<p style='{label_style}'>Today's Tasks</p>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        tasks = fetch_query("SELECT task_name FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
        if tasks:
            for tname in tasks:
                st.markdown(f"<p style='margin:0 0 4px 0; font-size:15px; color:white;'>{tname[0]}</p>", unsafe_allow_html=True)
        else:
            st.caption("No tasks for today.")

with b2:
    with st.container(border=True):
        st.markdown(f"<p style='{label_style}'>Upcoming Calendar</p>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        events = fetch_query("""
            SELECT description, event_date FROM events 
            WHERE user_email=%s AND event_date >= %s 
            ORDER BY event_date ASC LIMIT 3
        """, (user, t_date))
        
        if events:
            for desc, edate in events:
                st.markdown(f"<p style='margin:0 0 6px 0; font-size:14px;'><b>{edate.strftime('%b %d')}</b>: {desc}</p>", unsafe_allow_html=True)
        else:
            st.caption("No upcoming events.")

with b3:
    with st.container(border=True):
        st.markdown(f"<p style='{label_style}'>Trajectory Progress</p>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        blueprint_tasks = fetch_query("""
            SELECT task_description, progress FROM future_tasks 
            WHERE user_email=%s AND progress < 100 
            ORDER BY progress DESC LIMIT 3
        """, (user,))
        
        if blueprint_tasks:
            for desc, prog in blueprint_tasks:
                st.markdown(f"<p style='margin:0 0 6px 0; font-size:14px;'><b>{int(prog)}%</b>: {desc.upper()}</p>", unsafe_allow_html=True)
        else:
            st.caption("Strategy Map Clear.")

# --- FINANCIAL STATUS ---
st.markdown("### Financial Status")
f1, f2 = st.columns(2)
period = t_date.strftime("%B %Y")

with f1:
    with st.container(border=True):
        budget_calc = fetch_query("SELECT SUM(COALESCE(plan, 0) - COALESCE(actual, 0)) FROM finances WHERE user_email=%s AND period=%s", (user, period))
        rem = budget_calc[0][0] if budget_calc and budget_calc[0][0] is not None else 0
        st.markdown(f"<p style='color:gray;margin:0;'>Remaining Budget ({period})</p><h2 style='color:#76b372;margin:0;'>₹ {rem:,.2f}</h2>", unsafe_allow_html=True)

with f2:
    with st.container(border=True):
        debt_calc = fetch_query("SELECT SUM(COALESCE(amount, 0) - COALESCE(paid_out, 0)) FROM debt WHERE user_email=%s", (user,))
        net_debt = debt_calc[0][0] if debt_calc and debt_calc[0][0] is not None else 0
        st.markdown(f"<p style='color:gray;margin:0;'>Total Net Debt</p><h2 style='color:#ff4b4b;margin:0;'>₹ {net_debt:,.2f}</h2>", unsafe_allow_html=True)

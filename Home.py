import streamlit as st
import hashlib
import jwt
import datetime
from datetime import datetime as dt, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar
from streamlit_cookies_controller import CookieController

# --- JWT CONFIGURATION ---
JWT_SECRET = "ethos_super_secret_key_123" 
JWT_ALGO = "HS256"

st.set_page_config(layout="wide", page_title="Ethos Hub", page_icon="🛡️")
controller = CookieController()
cookie_name = "ethos_user_token"

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_jwt(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["email"]
    except:
        return None

# --- AUTHENTICATION LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    try:
        token = controller.get(cookie_name)
        if token:
            email = verify_jwt(token)
            if email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
    except:
        pass

if not st.session_state.logged_in:
    st.title("🛡️ ETHOS SYSTEM ACCESS")
    tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])
    
    with tab1:
        email_in = st.text_input("Email", key="login_email")
        pass_in = st.text_input("Password", type='password', key="login_pass")
        if st.button("INITIATE SESSION", use_container_width=True, type="primary"):
            res = fetch_query("SELECT password FROM users WHERE email=%s", (email_in,))
            if res and res[0][0] == make_hashes(pass_in):
                token = create_jwt(email_in)
                st.session_state.logged_in = True
                st.session_state.user_email = email_in
                controller.set(cookie_name, token)
                st.rerun() 
            else:
                st.error("Access Denied: Invalid Credentials")
    
    with tab2:
        st.subheader("New Identity Registration")
        new_email = st.text_input("Email", key="signup_email")
        new_pass = st.text_input("Password", type='password', key="signup_pass")
        if st.button("CREATE ACCOUNT", use_container_width=True):
            try:
                execute_query("INSERT INTO users (email, password) VALUES (%s, %s)", (new_email, make_hashes(new_pass)))
                st.success("Identity Created. Proceed to Login.")
            except:
                st.error("Identity already exists in database.")
    st.stop() 


# --- INITIALIZATION ---
user = st.session_state.user_email
render_sidebar()
now = dt.now() 
t_date = now.date()
t_time = now.strftime("%H:%M")
d_idx = t_date.weekday()
w_start = t_date - timedelta(days=d_idx)

# --- INNOVATIVE UI STYLING ---
st.markdown(f"""
    <style>
    .ethos-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(118, 179, 114, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.3s ease-in-out;
    }}
    .ethos-card:hover {{
        border: 1px solid rgba(118, 179, 114, 0.6);
        background: rgba(118, 179, 114, 0.02);
    }}
    .card-label {{
        color: #76b372;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }}
    .task-item {{
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 14px;
    }}
    .status-pip {{
        height: 6px; width: 6px;
        background-color: #76b372;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 5px #76b372;
    }}
    .metric-val {{ font-size: 24px; font-weight: bold; color: white; }}
    .metric-sub {{ font-size: 12px; color: gray; }}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ ETHOS COMMAND")
st.caption(f"SYSTEM STATUS: ACTIVE | {now.strftime('%H:%M:%S')} | {t_date}")

# --- ROW 1: THE EXECUTION LAYER ---
r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    st.markdown('<div class="ethos-card"><div class="card-label">Protocol: Today\'s Tasks</div>', unsafe_allow_html=True)
    tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
    if tasks:
        for tname, tdone in tasks[:5]: 
            color = "gray" if tdone else "white"
            st.markdown(f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{tname[0].upper()}</span></div>', unsafe_allow_html=True)
    else: st.caption("No tasks scheduled.")
    st.markdown('</div>', unsafe_allow_html=True)

with r1_c2:
    st.markdown('<div class="ethos-card"><div class="card-label">Timeline: Next Activities</div>', unsafe_allow_html=True)
    activities = fetch_query("""
        SELECT activity_name, start_time FROM timetable 
        WHERE user_email=%s AND day_index=%s AND start_time > %s 
        ORDER BY start_time ASC LIMIT 3
    """, (user, d_idx, t_time))
    if activities:
        for name, start in activities:
            st.markdown(f'<div class="task-item"><span style="color:#76b372; margin-right:10px;">{start}</span> {name[0].upper()}</div>', unsafe_allow_html=True)
    else: st.caption("Timeline clear for today.")
    st.markdown('</div>', unsafe_allow_html=True)

with r1_c3:
    st.markdown('<div class="ethos-card"><div class="card-label">Blueprint: Future Path</div>', unsafe_allow_html=True)
    blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 3", (user,))
    if blueprint:
        for desc, prog in blueprint:
            st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex; justify-content:space-between; font-size:12px;"><span>{desc[0][:20].upper()}</span><span>{int(prog[0])}%</span></div><div style="background:#333; height:4px; border-radius:2px;"><div style="background:#76b372; width:{prog[0]}%; height:4px; border-radius:2px;"></div></div></div>', unsafe_allow_html=True)
    else: st.caption("No active blueprint tasks.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 2: THE INTELLIGENCE LAYER ---
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    st.markdown('<div class="ethos-card"><div class="card-label">Capital: Liquidity & Debt</div>', unsafe_allow_html=True)
    period = t_date.strftime("%B %Y")
    budget = fetch_query("SELECT SUM(plan - actual) FROM finances WHERE user_email=%s AND period=%s", (user, period))
    rem_cash = budget[0][0] if budget and budget[0][0] else 0
    debt = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user,))
    net_debt = debt[0][0] if debt and debt[0][0] else 0
    
    st.markdown(f'<div class="metric-val">₹ {rem_cash:,.0f}</div><div class="metric-sub">Remaining Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="margin-top:10px;" class="metric-val" style="color:#ff4b4b;">₹ {net_debt:,.0f}</div><div class="metric-sub">Net Liability</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2_c2:
    st.markdown('<div class="ethos-card"><div class="card-label">Neural Lock: Output Today</div>', unsafe_allow_html=True)
    logs = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = %s", (user, t_date))
    if logs:
        for tname, mins in logs:
            st.markdown(f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;"><span>{tname[0].upper()}</span><span style="color:#76b372;">{mins[0]}m</span></div>', unsafe_allow_html=True)
    else: st.caption("No neural work logged today.")
    st.markdown('</div>', unsafe_allow_html=True)

with r2_c3:
    st.markdown('<div class="ethos-card"><div class="card-label">Calendar: Events</div>', unsafe_allow_html=True)
    events = fetch_query("SELECT description, event_date FROM events WHERE user_email=%s AND event_date >= %s ORDER BY event_date ASC LIMIT 3", (user, t_date))
    if events:
        for desc, edate in events:
            st.markdown(f'<div class="task-item"><div class="status-pip"></div><b>{edate[0].strftime("%b %d")}</b>: {desc[0]}</div>', unsafe_allow_html=True)
    else: st.caption("Calendar clear.")
    st.markdown('</div>', unsafe_allow_html=True)

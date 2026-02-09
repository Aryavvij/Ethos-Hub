import streamlit as st
import hashlib
import jwt
import datetime
from datetime import datetime as dt, timedelta
from database import execute_query, fetch_query
from utils import render_sidebar
from streamlit_cookies_controller import CookieController

# --- CONFIGURATION ---
JWT_SECRET = "ethos_super_secret_key_123" 
JWT_ALGO = "HS256"
ETHOS_GREEN = "#76b372"

st.set_page_config(layout="wide", page_title="Ethos Hub", page_icon="🛡️")
controller = CookieController()
cookie_name = "ethos_user_token"

# --- UTILITY FUNCTIONS ---
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
    st.markdown(f"""
        <style>
        div.stButton > button[kind="primary"] {{
            background-color: {ETHOS_GREEN};
            border-color: {ETHOS_GREEN};
            color: white;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("ETHOS SYSTEM ACCESS")
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

# --- UI STYLING ---
st.markdown(f"""
    <style>
    .ethos-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(118, 179, 114, 0.15);
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        min-height: 200px;
        transition: 0.3s ease;
    }}
    .ethos-card:hover {{
        border: 1px solid rgba(118, 179, 114, 0.4);
        background: rgba(118, 179, 114, 0.02);
    }}
    .card-label {{
        color: {ETHOS_GREEN};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 18px;
        opacity: 0.9;
    }}
    .task-item {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        font-size: 14px;
    }}
    .status-pip {{
        height: 6px; width: 6px;
        background-color: {ETHOS_GREEN};
        border-radius: 50%;
        margin-right: 12px;
        box-shadow: 0 0 5px {ETHOS_GREEN};
    }}
    .metric-val {{ font-size: 22px; font-weight: 700; color: white; }}
    .metric-sub {{ font-size: 11px; color: #888; text-transform: uppercase; margin-top: 2px; }}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ ETHOS COMMAND")
st.caption(f"SYSTEM STATUS: ACTIVE | {now.strftime('%H:%M:%S')} | {t_date}")

# --- ROW 1: THE EXECUTION LAYER ---
r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Protocol: Today\'s Tasks</div>', unsafe_allow_html=True)
    tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
    if tasks:
        for row in tasks[:5]:
            tname, tdone = row[0], row[1]
            color = "gray" if tdone else "white"
            st.markdown(f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{str(tname).upper()}</span></div>', unsafe_allow_html=True)
    else: st.caption("No tasks scheduled.")
    st.markdown('</div>', unsafe_allow_html=True)

with r1_c2:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Timeline: Next Activities</div>', unsafe_allow_html=True)
    activities = fetch_query("""
        SELECT task_name, start_time FROM timetable 
        WHERE user_email=%s AND day_index=%s AND start_time > %s 
        ORDER BY start_time ASC LIMIT 3
    """, (user, d_idx, t_time))
    if activities:
        for row in activities:
            st.markdown(f'<div class="task-item"><span style="color:{ETHOS_GREEN}; font-weight:bold; margin-right:12px;">{row[1]}</span> {str(row[0]).upper()}</div>', unsafe_allow_html=True)
    else: st.caption("Timeline clear.")
    st.markdown('</div>', unsafe_allow_html=True)

with r1_c3:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Blueprint: Future Path</div>', unsafe_allow_html=True)
    blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 3", (user,))
    if blueprint:
        for row in blueprint:
            desc, prog = row[0], int(row[1])
            st.markdown(f'''
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:5px;">
                        <span>{str(desc)[:20].upper()}</span><span>{prog}%</span>
                    </div>
                    <div style="background:#333; height:4px; border-radius:2px;">
                        <div style="background:{ETHOS_GREEN}; width:{prog}%; height:4px; border-radius:2px;"></div>
                    </div>
                </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 2: THE INTELLIGENCE LAYER ---
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Capital: Liquidity & Debt</div>', unsafe_allow_html=True)
    period = t_date.strftime("%B %Y")
    budget = fetch_query("SELECT SUM(plan - actual) FROM finances WHERE user_email=%s AND period=%s", (user, period))
    rem_cash = budget[0][0] if budget and budget[0][0] else 0
    debt = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user,))
    net_debt = debt[0][0] if debt and debt[0][0] else 0
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'<div class="metric-val" style="color:{ETHOS_GREEN};">₹{rem_cash:,.0f}</div><div class="metric-sub">Budget</div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-val" style="color:#ff4b4b;">₹{net_debt:,.0f}</div><div class="metric-sub">Liability</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r2_c2:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Neural Lock: Output Today</div>', unsafe_allow_html=True)
    logs = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = %s", (user, t_date))
    if logs:
        for row in logs:
            st.markdown(f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;"><span>{str(row[0]).upper()}</span><span style="color:{ETHOS_GREEN}; font-weight:bold;">{row[1]}m</span></div>', unsafe_allow_html=True)
    else: st.caption("No focus work logged.")
    st.markdown('</div>', unsafe_allow_html=True)

with r2_c3:
    st.markdown(f'<div class="ethos-card"><div class="card-label">Calendar: Events</div>', unsafe_allow_html=True)
    events = fetch_query("SELECT description, event_date FROM events WHERE user_email=%s AND event_date >= %s ORDER BY event_date ASC LIMIT 3", (user, t_date))
    if events:
        for row in events:
            date_str = row[1].strftime("%b %d")
            st.markdown(f'<div class="task-item"><div class="status-pip"></div><b>{date_str}</b>: {str(row[0])}</div>', unsafe_allow_html=True)
    else: st.caption("No upcoming events.")
    st.markdown('</div>', unsafe_allow_html=True)

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

st.title("ETHOS COMMAND")
st.caption(f"SYSTEM STATUS: ACTIVE | {now.strftime('%H:%M:%S')} | {t_date}")

# --- ROW 1: THE EXECUTION LAYER ---
r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
    content = ""
    if tasks:
        for row in tasks[:5]: 
            t_name, t_done = row[0], row[1]
            color = "gray" if t_done else "white"
            content += f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{t_name.upper()}</span></div>'
    else:
        content = '<p style="color:gray; font-size:12px;">No tasks scheduled.</p>'
    
    st.markdown(f'<div class="ethos-card"><div class="card-label">Work: Today\'s Tasks</div>{content}</div>', unsafe_allow_html=True)

with r1_c2:
    activities = fetch_query("""
        SELECT subject, start_time FROM timetable 
        WHERE user_email=%s AND day_name=%s AND start_time > %s 
        ORDER BY start_time ASC LIMIT 3
    """, (user, dt.now().strftime('%A'), t_time))
    
    content = ""
    if activities:
        for row in activities:
            s_name, s_time = row[0], row[1]
            content += f'<div class="task-item"><span style="color:#76b372; margin-right:10px;">{s_time}</span> {s_name.upper()}</div>'
    else:
        content = '<p style="color:gray; font-size:12px;">Timeline clear.</p>'
    
    st.markdown(f'<div class="ethos-card"><div class="card-label">Timetable: Upcoming Activities</div>{content}</div>', unsafe_allow_html=True)

with r1_c3:
    blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 3", (user,))
    content = ""
    if blueprint:
        for row in blueprint:
            b_desc, b_prog = row[0], row[1]
            content += f'''
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                        <span>{b_desc[:20].upper()}</span><span>{int(b_prog)}%</span>
                    </div>
                    <div style="background:#333; height:4px; border-radius:2px;">
                        <div style="background:#76b372; width:{b_prog}%; height:4px; border-radius:2px;"></div>
                    </div>
                </div>'''
    else:
        content = '<p style="color:gray; font-size:12px;">No active path.</p>'
        
    st.markdown(f'<div class="ethos-card"><div class="card-label">Blueprint: Future Tasks</div>{content}</div>', unsafe_allow_html=True)

# --- ROW 2: THE INTELLIGENCE LAYER ---
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    period = t_date.strftime("%B %Y")
    budget_data = fetch_query("SELECT SUM(plan - actual) FROM finances WHERE user_email=%s AND period=%s", (user, period))
    rem_cash = budget_data[0][0] if budget_data and budget_data[0][0] is not None else 0
    
    debt_data = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user,))
    net_debt = debt_data[0][0] if debt_data and debt_data[0][0] is not None else 0
    
    content = f'''
        <div class="metric-val">₹ {rem_cash:,.0f}</div><div class="metric-sub">Remaining Budget</div>
        <div style="margin-top:15px;" class="metric-val" style="color:#ff4b4b;">₹ {net_debt:,.0f}</div><div class="metric-sub">Net Liability</div>
    '''
    st.markdown(f'<div class="ethos-card"><div class="card-label">Financial: Budget & Debt</div>{content}</div>', unsafe_allow_html=True)

with r2_c2:
    logs = fetch_query("SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date = %s", (user, t_date))
    content = ""
    if logs:
        for row in logs:
            f_name, f_mins = row[0], row[1]
            content += f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;"><span>{f_name.upper()}</span><span style="color:#76b372;">{f_mins}m</span></div>'
    else:
        content = '<p style="color:gray; font-size:12px;">No output logged.</p>'
        
    st.markdown(f'<div class="ethos-card"><div class="card-label">Neural Lock: Output Today</div>{content}</div>', unsafe_allow_html=True)

with r2_c3:
    events = fetch_query("SELECT description, event_date FROM events WHERE user_email=%s AND event_date >= %s ORDER BY event_date ASC LIMIT 3", (user, t_date))
    content = ""
    if events:
        for row in events:
            e_desc, e_date = row[0], row[1]
            content += f'<div class="task-item"><div class="status-pip"></div><b>{e_date.strftime("%b %d")}</b>: {e_desc}</div>'
    else:
        content = '<p style="color:gray; font-size:12px;">Calendar clear.</p>'
        
    st.markdown(f'<div class="ethos-card"><div class="card-label">Calendar: Events</div>{content}</div>', unsafe_allow_html=True)

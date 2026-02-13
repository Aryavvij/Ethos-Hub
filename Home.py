import streamlit as st
import hashlib
import jwt
import datetime
from datetime import datetime as dt, timedelta
from database import fetch_query, execute_query
from utils import render_sidebar, check_rate_limit 
from services import FocusService, FinanceService
from streamlit_cookies_controller import CookieController
from pydantic import BaseModel, ValidationError

# --- 1. CONFIGURATION ---
JWT_SECRET = "ethos_super_secret_key_123" 
JWT_ALGO = "HS256"
ETHOS_GREEN = "#76b372"

st.set_page_config(layout="wide", page_title="Ethos Hub", page_icon="🛡️")
controller = CookieController()
cookie_name = "ethos_user_token"

# --- 2. AUTH UTILITIES ---
def create_jwt(email):
    payload = {"email": email, "exp": dt.utcnow() + timedelta(days=30)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        email = payload["email"]
        exp_ts = payload.get('exp')
        needs_refresh = (exp_ts - dt.utcnow().timestamp()) < (5 * 86400)
        return email, needs_refresh
    except: 
        return None, False

# --- 3. PERSISTENT AUTHENTICATION FLOW ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    token = controller.get(cookie_name)
    if token:
        email, refresh_needed = verify_jwt(token)
        if email:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            if refresh_needed:
                controller.set(cookie_name, create_jwt(email))
            st.rerun()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown(f"""<style>div.stButton > button[kind="primary"] {{ background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(118, 179, 114, 0.2) !important; color: white !important; border-radius: 8px !important; transition: all 0.3s ease !important; height: 3rem !important; }}</style>""", unsafe_allow_html=True)
    
    st.title("ETHOS SYSTEM ACCESS")
    t1, t2 = st.tabs(["LOGIN", "SIGN UP"])
    
    with t1:
        e_in = st.text_input("Email", key="l_e", autocomplete="username")
        p_in = st.text_input("Password", type='password', key="l_p", autocomplete="current-password")
        
        if st.button("INITIATE SESSION", use_container_width=True, type="primary"):
            if not check_rate_limit(limit=5, window=60):
                st.error("Too many attempts. System cooling down for 60s.")
            else:
                res = fetch_query("SELECT password FROM users WHERE email=%s", (e_in,))
                if res and res[0][0] == hashlib.sha256(p_in.encode()).hexdigest():
                    st.session_state.logged_in = True
                    st.session_state.user_email = e_in
                    controller.set(cookie_name, create_jwt(e_in))
                    st.rerun()
                else: 
                    st.error("Wrong Password or Username")
    
    with t2:
        st.info("Registration requires administrator clearance.")
        
    st.stop()

# --- 4. DASHBOARD RENDERING ---
user = st.session_state.user_email
render_sidebar()
now = dt.now()
t_date = now.date()
d_idx = t_date.weekday()
w_start = t_date - timedelta(days=d_idx)

st.markdown(f"""
    <style>
    .ethos-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(118, 179, 114, 0.15);
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        min-height: 220px;
        transition: 0.3s ease;
    }}
    .ethos-card:hover {{ border-color: {ETHOS_GREEN}; background: rgba(118, 179, 114, 0.05); }}
    .card-label {{ color: {ETHOS_GREEN}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 18px; }}
    .task-item {{ display: flex; align-items: center; margin-bottom: 10px; font-size: 14px; }}
    .status-pip {{ height: 6px; width: 6px; background-color: {ETHOS_GREEN}; border-radius: 50%; margin-right: 12px; box-shadow: 0 0 5px {ETHOS_GREEN}; }}
    .metric-val {{ font-size: 24px; font-weight: 700; color: white; }}
    .metric-sub {{ font-size: 11px; color: #888; text-transform: uppercase; }}
    </style>
""", unsafe_allow_html=True)

st.title("ETHOS COMMAND")
st.caption(f"SYSTEM STATUS: ACTIVE | {now.strftime('%H:%M:%S')} | {t_date.strftime('%A, %b %d')}")

# --- 5. GRID LAYOUT ---
r1_c1, r1_c2, r1_c3 = st.columns(3)

class TaskSchema(BaseModel):
    name: str
    is_done: bool

with r1_c1: # PROTOCOL CARD
    raw_tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
    content = ""
    for row in raw_tasks[:5]:
        try:
            t = TaskSchema(name=row[0], is_done=row[1]) 
            color = "gray" if t.is_done else "white"
            content += f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{t.name.upper()}</span></div>'
        except ValidationError: continue
    
    st.markdown(f'<div class="ethos-card"><div class="card-label">Work: Today\'s Tasks</div>{content or "Clear"}</div>', unsafe_allow_html=True)

with r1_c2: # TIMELINE CARD 
    current_day_name = now.strftime('%A')
    t_time = now.strftime('%H:%M:%S')
    
    all_today = fetch_query("SELECT subject, start_time FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC", (user, current_day_name))
    
    future_acts = [row for row in all_today if str(row[1]) >= t_time]
    display_acts = future_acts[:4] if len(future_acts) >= 1 else all_today[-5:]
    
    content = "".join([f'<div class="task-item"><span style="color:{ETHOS_GREEN}; margin-right:10px;">{row[1]}</span> {row[0].upper()}</div>' for row in display_acts])
    st.markdown(f'<div class="ethos-card"><div class="card-label">Timeline: Current & Upcoming</div>{content or "Day Complete"}</div>', unsafe_allow_html=True)

with r1_c3: # BLUEPRINT CARD (Updated to 4 tasks)
    blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 4", (user,))
    content = ""
    for desc, prog in blueprint:
        content += f'''<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;"><span>{desc[:20].upper()}</span><span>{int(prog)}%</span></div>
                    <div style="background:#333; height:4px; border-radius:2px;"><div style="background:{ETHOS_GREEN}; width:{prog}%; height:4px; border-radius:2px;"></div></div></div>'''
    st.markdown(f'<div class="ethos-card"><div class="card-label">Blueprint: Future Path</div>{content or "Clear"}</div>', unsafe_allow_html=True)

r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1: # FINANCIAL CARD
    fin_metrics = FinanceService.get_dashboard_metrics(user, t_date.strftime("%B %Y"))
    st.markdown(f'''<div class="ethos-card"><div class="card-label">Financial: Budget & Debt</div>
                <div class="metric-val">₹ {fin_metrics.remaining_budget:,.0f}</div><div class="metric-sub">Remaining Budget</div>
                <div style="margin-top:15px;" class="metric-val" style="color:#ff4b4b;">₹ {fin_metrics.net_debt:,.0f}</div><div class="metric-sub">Net Liability</div></div>''', unsafe_allow_html=True)

with r2_c2: # NEURAL LOCK CARD
    logs = FocusService.get_daily_logs(user, t_date)
    content = "".join([f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;"><span>{row.task_name.upper()}</span><span style="color:{ETHOS_GREEN};">{row.duration_mins}m</span></div>' for row in logs])
    st.markdown(f'<div class="ethos-card"><div class="card-label">Neural Lock: Output Today</div>{content or "No focus logs"}</div>', unsafe_allow_html=True)

with r2_c3: # EVENTS CARD 
    events = fetch_query("SELECT description, event_date FROM events WHERE user_email=%s AND event_date >= %s ORDER BY event_date ASC LIMIT 4", (user, t_date))
    content = "".join([f'<div class="task-item"><div class="status-pip"></div><b>{row[1].strftime("%b %d")}</b>: {row[0]}</div>' for row in events])
    st.markdown(f'<div class="ethos-card"><div class="card-label">Calendar: Upcoming Events</div>{content or "Clear"}</div>', unsafe_allow_html=True)

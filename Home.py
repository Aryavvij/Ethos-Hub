import streamlit as st
import hashlib
import jwt
import html
import traceback
from datetime import datetime as dt, timedelta
from database import fetch_query, execute_query
from utils import render_sidebar, check_rate_limit 
from streamlit_cookies_controller import CookieController
from pydantic import BaseModel, ValidationError
from services.logic import FocusService, FinanceService
from services.observability import Telemetry

# --- 1. CONFIGURATION ---
JWT_SECRET = "ethos_super_secret_key_123" 
JWT_ALGO = "HS256"
ETHOS_GREEN = "#76b372"

st.set_page_config(layout="wide", page_title="Ethos Hub", page_icon="🛡️")

# Initialize controller only if needed to prevent JS bloat
if 'controller' not in st.session_state:
    st.session_state.controller = CookieController()
controller = st.session_state.controller
cookie_name = "ethos_user_token"

# --- 2. AUTH UTILITIES ---
def create_jwt(email):
    return jwt.encode({"email": email, "exp": dt.utcnow() + timedelta(days=30)}, JWT_SECRET, algorithm=JWT_ALGO)

# --- 3. PERSISTENT AUTHENTICATION FLOW ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    try:
        all_cookies = controller.get_all()
        if all_cookies and cookie_name in all_cookies:
            token = all_cookies.get(cookie_name)
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            if payload and "email" in payload:
                st.session_state.logged_in = True
                st.session_state.user_email = payload["email"]
                st.rerun()
    except:
        pass 

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("ETHOS SYSTEM ACCESS")
    
    with st.form("login_form", clear_on_submit=False):
        e_in = st.text_input("Email", autocomplete="username")
        p_in = st.text_input("Password", type='password', autocomplete="current-password")
        submit = st.form_submit_button("INITIATE SESSION", use_container_width=True)
        
        if submit:
            with st.spinner("⚡ CONTACTING NEURAL SHARD..."):
                res = fetch_query("SELECT password, role FROM users WHERE email=%s LIMIT 1", (e_in,))
                
                if res and res[0][0] == hashlib.sha256(p_in.encode()).hexdigest():
                    st.session_state.logged_in = True
                    st.session_state.user_email = e_in
                    st.session_state.role = res[0][1] if len(res[0]) > 1 else "user"
                    controller.set(cookie_name, create_jwt(e_in))
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
    st.stop()

# --- 4. DASHBOARD RENDERING ---
try:
    user = st.session_state.user_email
    render_sidebar()
    
    now = dt.now()
    t_date = now.date()
    d_idx = t_date.weekday()
    w_start = t_date - timedelta(days=d_idx)

    # CSS for Neural Cards
    st.markdown(f"""
        <style>
        .ethos-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(118, 179, 114, 0.15);
            border-radius: 12px;
            padding: 22px; margin-bottom: 20px; height: 280px;
            overflow: hidden;
            transition: 0.3s ease;
        }}
        .ethos-card:hover {{ border-color: {ETHOS_GREEN}; background: rgba(118, 179, 114, 0.05); }}
        .card-label {{ color: {ETHOS_GREEN}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px; }}
        .task-item {{ display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; color: white; }}
        .status-pip {{ height: 6px; width: 6px; background-color: {ETHOS_GREEN}; border-radius: 50%; margin-right: 12px; }}
        .metric-val {{ font-size: 24px; font-weight: 700; color: white; }}
        .metric-sub {{ font-size: 11px; color: #888; text-transform: uppercase; }}
        </style>
    """, unsafe_allow_html=True)

    st.title("ETHOS COMMAND")
    st.caption(f"CONNECTED: {user.upper()} | {t_date.strftime('%A, %b %d')}")

    # --- ROW 1 ---
    r1_c1, r1_c2, r1_c3 = st.columns(3)

    with r1_c1: # PROTOCOL CARD
        raw_tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s LIMIT 5", (user, d_idx, w_start))
        content = ""
        for row in (raw_tasks or []):
            safe_name = html.escape(row[0]) 
            color = "gray" if row[1] else "white"
            content += f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{safe_name.upper()}</span></div>'
        st.markdown(f'<div class="ethos-card"><div class="card-label">Work: Today\'s Tasks</div>{content or "Clear"}</div>', unsafe_allow_html=True)

    with r1_c2: # TIMELINE CARD
        current_day_name = now.strftime('%A')
        all_today = fetch_query("SELECT subject, start_time FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC LIMIT 5", (user, current_day_name))
        content = ""
        for row in (all_today or []):
            safe_sub = html.escape(str(row[0]))
            content += f'<div class="task-item"><span style="color:{ETHOS_GREEN}; margin-right:10px;">{row[1]}</span> {safe_sub.upper()}</div>'
        st.markdown(f'<div class="ethos-card"><div class="card-label">Timeline: Schedule</div>{content or "No Activities"}</div>', unsafe_allow_html=True)

    with r1_c3: # BLUEPRINT CARD
        blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 4", (user,))
        content = ""
        for desc, prog in (blueprint or []):
            safe_desc = html.escape(desc[:20]) 
            content += f'''<div style="margin-bottom:15px;"><div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;"><span>{safe_desc.upper()}</span><span>{int(prog)}%</span></div>
                        <div style="background:#333; height:4px; border-radius:2px;"><div style="background:{ETHOS_GREEN}; width:{prog}%; height:4px; border-radius:2px;"></div></div></div>'''
        st.markdown(f'<div class="ethos-card"><div class="card-label">Blueprint: Future Path</div>{content or "Clear"}</div>', unsafe_allow_html=True)

    # --- ROW 2 (THE RESTORED BOXES) ---
    r2_c1, r2_c2, r2_c3 = st.columns(3)

    with r2_c1: # FINANCIAL CARD
        fin_metrics = FinanceService.get_dashboard_metrics(user, t_date.strftime("%B %Y"))
        st.markdown(f'''<div class="ethos-card"><div class="card-label">Financial: Budget & Debt</div>
                    <div class="metric-val">₹ {fin_metrics.remaining_budget:,.0f}</div><div class="metric-sub">Remaining Budget</div>
                    <div style="margin-top:25px;" class="metric-val" style="color:#ff4b4b;">₹ {fin_metrics.net_debt:,.0f}</div><div class="metric-sub">Net Liability</div></div>''', unsafe_allow_html=True)

    with r2_c2: # NEURAL LOCK (FOCUS) CARD
        logs = FocusService.get_daily_logs(user, t_date)
        content = ""
        for row in (logs or [])[:6]:
            safe_log_name = html.escape(row.task_name)
            content += f'<div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:12px;"><span>{safe_log_name.upper()}</span><span style="color:{ETHOS_GREEN};">{row.duration_mins}m</span></div>'
        st.markdown(f'<div class="ethos-card"><div class="card-label">Neural Lock: Output Today</div>{content or "No focus logs"}</div>', unsafe_allow_html=True)

    with r2_c3: # EVENTS CARD
        events = fetch_query("SELECT description, event_date FROM events WHERE user_email=%s AND event_date >= %s ORDER BY event_date ASC LIMIT 5", (user, t_date))
        content = ""
        for row in (events or []):
            safe_evt = html.escape(row[0])
            content += f'<div class="task-item"><div class="status-pip"></div><b>{row[1].strftime("%b %d")}</b>: {safe_evt}</div>'
        st.markdown(f'<div class="ethos-card"><div class="card-label">Calendar: Upcoming Events</div>{content or "Clear"}</div>', unsafe_allow_html=True)

except Exception as e:
    # Error telemetry for troubleshooting
    error_details = {"error": str(e), "stack_trace": traceback.format_exc()}
    Telemetry.log('ERROR', 'Home_Render_Failure', metadata=error_details)
    st.error(f"ETHOS: A neural glitch occurred.")
    if st.button("RE-INITIALIZE"):
        st.rerun()

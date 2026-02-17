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

# Initialize cookie controller to persist session
if 'controller' not in st.session_state:
    st.session_state.controller = CookieController()
controller = st.session_state.controller
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
    try:
        all_cookies = controller.get_all()
        if all_cookies and cookie_name in all_cookies:
            token = all_cookies.get(cookie_name)
            email, refresh_needed = verify_jwt(token)
            
            if email:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                if refresh_needed:
                    controller.set(cookie_name, create_jwt(email))
                st.rerun()
    except Exception:
        pass 

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown(f"""<style>
        div.stButton > button[kind="primary"] {{ 
            background-color: rgba(255, 255, 255, 0.05) !important; 
            border: 1px solid {ETHOS_GREEN}77 !important; 
            color: white !important; 
            border-radius: 8px !important; 
            height: 3.5rem !important;
            transition: all 0.3s ease;
        }}
        div.stButton > button[kind="primary"]:hover {{
            background-color: rgba(118, 179, 114, 0.1) !important;
            border-color: {ETHOS_GREEN} !important;
        }}
    </style>""", unsafe_allow_html=True)
    
    st.title("ETHOS SYSTEM ACCESS")
    t1, t2 = st.tabs(["LOGIN", "SIGN UP"])
    
    with t1:
        with st.form("login_form", clear_on_submit=False):
            e_in = st.text_input("Email", autocomplete="username")
            p_in = st.text_input("Password", type='password', autocomplete="current-password")
            submit = st.form_submit_button("INITIATE SESSION", use_container_width=True)
            
            if submit:
                if not check_rate_limit(limit=5, window=60):
                    st.error("Too many attempts. System cooling down.")
                else:
                    with st.status("Verifying Neural Link...", expanded=False) as status:
                        res = fetch_query("SELECT password, role FROM users WHERE email=%s", (e_in,))
                        
                        if res and res[0][0] == hashlib.sha256(p_in.encode()).hexdigest():
                            status.update(label="Access Granted. Syncing...", state="complete")
                            
                            st.session_state.logged_in = True
                            st.session_state.user_email = e_in
                            st.session_state.role = res[0][1] if len(res[0]) > 1 else "user"
                            
                            controller.set(cookie_name, create_jwt(e_in))
                            Telemetry.log('AUTH', 'Login_Success', metadata={'user': e_in})
                            st.rerun()
                        else: 
                            status.update(label="Access Denied.", state="error")
                            st.error("Invalid credentials.")
    
    with t2:
        st.info("Registration requires administrator clearance.")
    st.stop()

# --- 4. DASHBOARD RENDERING ---
try:
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
            padding: 22px; margin-bottom: 20px; height: 280px;
            transition: 0.3s ease; overflow-y: hidden;
        }}
        .ethos-card:hover {{ border-color: {ETHOS_GREEN}; background: rgba(118, 179, 114, 0.05); }}
        .card-label {{ color: {ETHOS_GREEN}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px; }}
        .task-item {{ display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; }}
        .status-pip {{ height: 6px; width: 6px; background-color: {ETHOS_GREEN}; border-radius: 50%; margin-right: 12px; }}
        .metric-val {{ font-size: 24px; font-weight: 700; color: white; }}
        </style>
    """, unsafe_allow_html=True)

    st.title("ETHOS COMMAND")
    st.caption(f"SYSTEM STATUS: ACTIVE | {now.strftime('%H:%M:%S')} | {t_date.strftime('%A, %b %d')}")

    # --- 5. GRID CONTENT ---
    r1_c1, r1_c2, r1_c3 = st.columns(3)

    class TaskSchema(BaseModel):
        name: str
        is_done: bool

    with r1_c1: # PROTOCOL CARD
        raw_tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
        content = ""
        for row in (raw_tasks or [])[:5]:
            try:
                t = TaskSchema(name=row[0], is_done=row[1]) 
                safe_name = html.escape(t.name) 
                color = "gray" if t.is_done else "white"
                content += f'<div class="task-item"><div class="status-pip"></div><span style="color:{color}">{safe_name.upper()}</span></div>'
            except ValidationError: continue
        st.markdown(f'<div class="ethos-card"><div class="card-label">Work: Today\'s Tasks</div>{content or "Clear"}</div>', unsafe_allow_html=True)

    with r1_c2: # TIMELINE CARD
        current_day_name = now.strftime('%A')
        t_time = now.strftime('%H:%M:%S')
        all_today = fetch_query("SELECT subject, start_time FROM timetable WHERE user_email=%s AND day_name=%s ORDER BY start_time ASC", (user, current_day_name))
        future_acts = [row for row in (all_today or []) if str(row[1]) >= t_time]
        display_acts = future_acts[:5] if len(future_acts) >= 1 else (all_today or [])[-5:]
        content = ""
        for row in display_acts:
            safe_sub = html.escape(str(row[0]))
            content += f'<div class="task-item"><span style="color:{ETHOS_GREEN}; margin-right:10px;">{row[1]}</span> {safe_sub.upper()}</div>'
        st.markdown(f'<div class="ethos-card"><div class="card-label">Timeline: Current & Upcoming</div>{content or "No Activities"}</div>', unsafe_allow_html=True)

    with r1_c3: # BLUEPRINT CARD
        blueprint = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 4", (user,))
        content = ""
        for desc, prog in (blueprint or []):
            safe_desc = html.escape(desc[:20]) 
            content += f'''<div style="margin-bottom:15px;"><div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;"><span>{safe_desc.upper()}</span><span>{int(prog)}%</span></div>
                        <div style="background:#333; height:4px; border-radius:2px;"><div style="background:{ETHOS_GREEN}; width:{prog}%; height:4px; border-radius:2px;"></div></div></div>'''
        st.markdown(f'<div class="ethos-card"><div class="card-label">Blueprint: Future Path</div>{content or "Clear"}</div>', unsafe_allow_html=True)

except Exception as e:
    Telemetry.log('ERROR', 'Global_System_Crash', metadata={"error": str(e), "page": "Home.py"})
    st.error("ETHOS: A neural glitch occurred. Recalibrating...")
    if st.button("RE-INITIALIZE"):
        st.rerun()

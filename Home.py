import streamlit as st
import hashlib
import jwt
import html
from datetime import datetime as dt, timedelta
from database import fetch_query, execute_query
from utils import render_sidebar, check_rate_limit 
from streamlit_cookies_controller import CookieController
from pydantic import BaseModel, ValidationError
from services.services import FocusService, FinanceService
from services.observability import Telemetry

# --- 1. CONFIGURATION ---
JWT_SECRET = "ethos_super_secret_key_123" 
JWT_ALGO = "HS256"
ETHOS_GREEN = "#76b372"

st.set_page_config(layout="wide", page_title="Ethos Hub", page_icon="🛡️")

# Initialize controller only once in session state
if 'controller' not in st.session_state:
    st.session_state.controller = CookieController()
controller = st.session_state.controller

# --- 2. AUTH UTILITIES ---
def create_jwt(email):
    return jwt.encode({"email": email, "exp": dt.utcnow() + timedelta(days=30)}, JWT_SECRET, algorithm=JWT_ALGO)

# --- 3. PERSISTENT AUTH FLOW ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Skip cookie check if already logged in to save time
if not st.session_state.logged_in:
    try:
        all_cookies = controller.get_all()
        if all_cookies and "ethos_user_token" in all_cookies:
            token = all_cookies.get("ethos_user_token")
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            st.session_state.logged_in = True
            st.session_state.user_email = payload["email"]
            st.rerun()
    except:
        pass 

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("ETHOS SYSTEM ACCESS")
    
    # Using a Form to block character-by-character reruns
    with st.form("login_form"):
        e_in = st.text_input("Email", autocomplete="username")
        p_in = st.text_input("Password", type='password', autocomplete="current-password")
        submit = st.form_submit_button("INITIATE SESSION", use_container_width=True)
        
        if submit:
            # Spinner is faster than status bar
            with st.spinner("⚡ CONTACTING NEURAL SHARD..."):
                # Single, optimized query
                res = fetch_query("SELECT password, role FROM users WHERE email=%s LIMIT 1", (e_in,))
                
                if res and res[0][0] == hashlib.sha256(p_in.encode()).hexdigest():
                    # 1. IMMEDIATE UI ESCALATION (Don't wait for logs)
                    st.session_state.logged_in = True
                    st.session_state.user_email = e_in
                    st.session_state.role = res[0][1] if len(res[0]) > 1 else "user"
                    
                    # 2. ASYNC COOKIE SET
                    controller.set("ethos_user_token", create_jwt(e_in))
                    
                    # 3. BACKGROUND LOGGING
                    Telemetry.log('AUTH', 'Login_Success', metadata={'user': e_in})
                    
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

    st.markdown(f"""
        <style>
        .ethos-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(118, 179, 114, 0.15);
            border-radius: 12px;
            padding: 22px; margin-bottom: 20px; height: 280px;
            overflow: hidden;
        }}
        .card-label {{ color: {ETHOS_GREEN}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px; }}
        .task-item {{ display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; color: white; }}
        .status-pip {{ height: 6px; width: 6px; background-color: {ETHOS_GREEN}; border-radius: 50%; margin-right: 12px; }}
        .metric-val {{ font-size: 24px; font-weight: 700; color: white; }}
        </style>
    """, unsafe_allow_html=True)

    st.title("ETHOS COMMAND")
    st.caption(f"SYSTEM STATUS: ACTIVE | {t_date.strftime('%A, %b %d')}")

    # --- 5. GRID CONTENT ---
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
    st.error("🛡️ ETHOS: A neural glitch occurred.")
    if st.button("RE-INITIALIZE"):
        st.rerun()

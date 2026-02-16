import streamlit as st
import time
from streamlit_cookies_controller import CookieController
import functools
import traceback
from services.observability import Telemetry

def ethos_observe(page_name):
    """Decorator to automatically track performance and catch errors for any page."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            Telemetry.log('AUTH', 'Page_Access', metadata={'page': page_name})
            
            # 1. Track Performance & Catch Crashes
            try:
                with Telemetry.track_latency(f"Page_Load: {page_name}"):
                    return func(*args, **kwargs)
            except Exception as e:
                # 2. Log Crash Details for Admin Page
                error_info = {
                    "error": str(e),
                    "stack_trace": traceback.format_exc(),
                    "page": page_name
                }
                Telemetry.log('ERROR', 'Global_Page_Crash', metadata=error_info)
                st.error(f"ETHOS: {page_name} link unstable. Recalibrating...")
                if st.button("RE-SYNC SYSTEM"):
                    st.rerun()
        return wrapper
    return decorator

def check_rate_limit(limit=10, window=60):
    """
    Limits a user to 'limit' actions every 'window' seconds.
    """
    if 'request_history' not in st.session_state:
        st.session_state.request_history = []

    current_time = time.time()
    st.session_state.request_history = [
        t for t in st.session_state.request_history if current_time - t < window
    ]

    if len(st.session_state.request_history) >= limit:
        return False 
    st.session_state.request_history.append(current_time)
    return True

def render_sidebar():
    controller = CookieController()
    cookie_name = "ethos_user_token"
    
    user = st.session_state.get('user_email', 'Unknown')
    
    with st.sidebar:
        st.markdown(f"""
            <div style="background: rgba(118, 179, 114, 0.1); 
                        padding: 12px; 
                        border-radius: 8px; 
                        border: 1px solid #76b372; 
                        margin-bottom: 20px;
                        text-align: center;">
                <span style="font-size: 14px; font-weight: 700; color: #76b372; word-wrap: break-word; text-transform: uppercase;">
                    {user}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # SECURE LOGOUT BUTTON
        if st.button("LOGOUT", use_container_width=True):

            controller.remove(cookie_name)
            st.session_state.logged_in = False
            st.session_state.user_email = None
            
            time.sleep(0.1) 
            st.rerun()

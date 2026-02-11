import streamlit as st
import time

def check_rate_limit(limit=10, window=60):
    """
    Limits a user to 'limit' actions every 'window' seconds.
    Default: 10 actions per minute.
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
    user = st.session_state.get('user_email', 'Unknown')
    with st.sidebar:
        st.markdown(f"""
            <div style="background: rgba(118, 179, 114, 0.1); 
                        padding: 12px; 
                        border-radius: 8px; 
                        border: 1px solid #76b372; 
                        margin-bottom: 10px;
                        text-align: center;">
                <span style="font-size: 14px; font-weight: 500; color: #76b372; word-wrap: break-word;">
                    {user}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.rerun()

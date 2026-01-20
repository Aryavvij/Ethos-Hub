import streamlit as st

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

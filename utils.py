import streamlit as st

def render_sidebar():
    user = st.session_state.get('user_email', 'Unknown')
    with st.sidebar:
        st.markdown(f"""
            <div style="background: rgba(118, 179, 114, 0.15); padding: 12px; border-radius: 5px; border: 1px solid #76b372; margin-bottom: 10px;">
                <p style="margin:0; font-size:10px; color:#76b372; font-weight:bold;">IDENTITY</p>
                <p style="margin:0; font-size:13px; overflow: hidden; text-overflow: ellipsis;">{user}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

import streamlit as st
from datetime import datetime
from database import execute_query, fetch_query

# --- GLOBAL SIDEBAR ---
with st.sidebar:
    st.success(f"Logged in: {st.session_state.user_email}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()
    st.markdown("---")

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

# --- SIDEBAR LOGOUT ---
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🧠 Daily Reflection")

user = st.session_state.user_email

# 1. DATE SELECTION: Choose any day to see history
col1, col2 = st.columns([1, 2])
with col1:
    selected_date = st.date_input("Viewing Date:", datetime.now().date())

# 2. FETCH DATA: Pull existing reflection for the selected date from Supabase
existing_entry = fetch_query(
    "SELECT content FROM reflections WHERE user_email=%s AND ref_date=%s",
    (user, selected_date)
)

# If data exists, use it; otherwise, start with an empty box
initial_content = existing_entry[0][0] if existing_entry else ""

# 3. TEXT AREA: Display and Edit
st.markdown(f"### Entry for {selected_date.strftime('%d %B, %Y')}")
reflection_text = st.text_area(
    "Write your thoughts, wins, and lessons for today:",
    value=initial_content,
    height=400,
    placeholder="What did you learn today? What are you grateful for?"
)

# 4. SAVE LOGIC: Push to Cloud
if st.button("💾 Save to Cloud"):
    if reflection_text:
        execute_query("""
            INSERT INTO reflections (user_email, ref_date, content)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_email, ref_date) 
            DO UPDATE SET content = EXCLUDED.content
        """, (user, selected_date, reflection_text))
        st.success(f"Reflection for {selected_date} saved successfully!")
    else:
        st.warning("Cannot save an empty reflection.")

st.write("---")
st.caption("Your data is synced with Supabase and will remain available across sessions.")

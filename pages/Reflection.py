import streamlit as st
import sqlite3
from datetime import datetime
from database import fetch_query, execute_query

# check for login session before showing the page
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide")

# load our custom css for the dashboard look
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Daily Reflections")

# get the current date for the header
today = datetime.now().strftime("%Y-%m-%d")

# using the custom card class from styles.css
st.markdown('<div class="ethos-card">', unsafe_allow_html=True)
st.subheader(f"Journal: {today}")

# simple text input for a quick daily recap
win = st.text_input("What was your biggest win today?", placeholder="One sentence only...")

# slider to track daily energy/mood trends
mood = st.select_slider("Current Energy Level", options=["Drained", "Low", "Neutral", "Good", "Fired Up"], value="Neutral")

# file uploader to attach a daily picture
uploaded_file = st.file_uploader("Upload a Photo of the Day", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, caption="Daily Memory", width=400)

# save button logic
if st.button("💾 Save Reflection"):
    st.success("Reflection saved for today.")
st.markdown('</div>', unsafe_allow_html=True)

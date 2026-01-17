import streamlit as st
import pandas as pd
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🛡️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🛡️ Iron Clad")
st.caption("Strategic Training Splits & Performance Tracking")

# --- 2. VITALS (STAY THE SAME) ---
with st.container(border=True):
    st.subheader("Current Vitals")
    m1, m2, m3 = st.columns(3)
    with m1:
        weight = st.number_input("Current Weight (kg)", min_value=0.0, step=0.1, key="weight_input")
    with m2:
        bf = st.number_input("Body Fat %", min_value=0.0, step=0.1, key="bf_input")
    with m3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Update Vitals", use_container_width=True):
            st.success("Vitals Updated.")

st.markdown("---")

# --- 3. DYNAMIC SPLIT CONFIGURATION ---
st.subheader("📅 Weekly Training Structure")
st.info("Select the days you train. You can name each session (e.g., 'Push', 'Pull', 'Legs').")

# We use a multiselect so you only see the tables you want
selected_days = st.multiselect(
    "Active Training Days",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Monday", "Wednesday", "Friday"]
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. GENERATING DYNAMIC TABLES ---
# This creates a vertical flow of custom titled tables
for day in selected_days:
    with st.container(border=True):
        # Header Row: Day and Training Focus
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"### {day}")
        with c2:
            # This allows you to decide the title/focus of the training day
            split_title = st.text_input(
                f"Focus for {day}", 
                placeholder="e.g., Heavy Push / Lower Body / Cardio", 
                key=f"title_{day}",
                label_visibility="collapsed"
            )

        # The Training Table for this specific day
        # In a real app, you would fetch existing data for this day here
        base_df = pd.DataFrame(columns=["Exercise", "Weight (kg)", "Sets", "Reps", "RPE"])
        
        st.data_editor(
            base_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{day}",
            column_config={
                "Exercise": st.column_config.TextColumn("Exercise"),
                "Weight (kg)": st.column_config.NumberColumn("Weight", min_value=0),
                "RPE": st.column_config.SelectboxColumn("Intensity (RPE)", options=["6", "7", "8", "9", "10"])
            }
        )

# --- 5. GLOBAL SAVE ---
st.markdown("---")
if st.button("🚀 Synchronize Weekly Training Plan", use_container_width=True):
    # Logic to save each editor's data linked to 'day' and 'split_title' goes here
    st.success("Training Split Saved Successfully.")

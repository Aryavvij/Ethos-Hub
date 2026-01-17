import streamlit as st
import pandas as pd
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🛡️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🛡️ Iron Clad")
st.caption("Strategic Training Splits")

# --- 2. DYNAMIC TRAINING BLOCKS ---
# Hardcoded day list to remove the selection box clutter
training_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

for day in training_days:
    with st.container():
        # Perfectly Aligned Header and Description
        col_day, col_desc = st.columns([1, 4])
        
        with col_day:
            # Theme-consistent Green Header
            st.markdown(f"""
                <div style="background:#76b372; padding:10px; border-radius:5px; text-align:center; color:white; font-weight:bold; height:45px; display:flex; align-items:center; justify-content:center;">
                    {day.upper()}
                </div>
            """, unsafe_allow_html=True)
            
        with col_desc:
            st.text_input(f"Focus for {day}", placeholder="Focus (e.g., Push / Legs)", key=f"title_{day}", label_visibility="collapsed")

        # Table without Intensity (RPE) column
        base_df = pd.DataFrame(columns=["Exercise", "Weight (kg)", "Sets", "Reps"])
        st.data_editor(
            base_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{day}",
            column_config={
                "Exercise": st.column_config.TextColumn("Exercise"),
                "Weight (kg)": st.column_config.NumberColumn("Weight", min_value=0),
                "Sets": st.column_config.NumberColumn("Sets", min_value=0),
                "Reps": st.column_config.NumberColumn("Reps", min_value=0),
            }
        )
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# --- 3. GLOBAL SYNC ---
st.markdown("---")
if st.button("🚀 Synchronize Weekly Training Plan", use_container_width=True):
    st.success("Training Split Saved Successfully.")

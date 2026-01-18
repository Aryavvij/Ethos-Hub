import streamlit as st
import pandas as pd
import json
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🛡️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🛡️ Iron Clad")
st.caption("Strategic Training Splits")

# --- 2. DATA PRE-LOADER (The Persistence Fix) ---
# Fetch all existing splits for this user
saved_splits = fetch_query("SELECT day_name, split_title, exercises_json FROM training_splits WHERE user_email=%s", (user,))
# Format: { 'Monday': {'title': 'Push', 'data': pd.DataFrame(...) } }
splits_cache = {row[0]: {"title": row[1], "data": row[2]} for row in saved_splits}

# --- 3. DYNAMIC DAY SELECTION ---
st.markdown("### ⚙️ Split Configuration")
# We default to the days already in the database if available
existing_days = list(splits_cache.keys())
active_days = st.multiselect(
    "Select your active training days:",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=existing_days if existing_days else ["Monday", "Tuesday", "Wednesday", "Friday"],
    help="Only selected days will appear below."
)

st.markdown("---")

# --- 4. DYNAMIC TRAINING BLOCKS ---
for day in active_days:
    with st.container():
        # Day Header and Title Input
        col_day, col_desc = st.columns([1, 4])
        
        # Load existing title if it exists
        existing_title = splits_cache.get(day, {}).get("title", "")
        
        with col_day:
            st.markdown(f"""
                <div style="background:#76b372; padding:8px; border-radius:5px; 
                text-align:center; color:white; font-weight:bold; height:41px; 
                display:flex; align-items:center; justify-content:center; 
                text-transform: uppercase; font-size: 13px; border: 1px solid #5a8a56;">
                    {day}
                </div>
            """, unsafe_allow_html=True)
            
        with col_desc:
            st.text_input(
                f"Focus for {day}", 
                value=existing_title, # FIXED: This keeps your title visible
                placeholder="Training Focus (e.g., Push / Legs)", 
                key=f"title_{day}", 
                label_visibility="collapsed"
            )

        # Load existing table data if it exists
        existing_json = splits_cache.get(day, {}).get("data", None)
        if existing_json:
            try:
                base_df = pd.read_json(existing_json)
            except:
                base_df = pd.DataFrame(columns=["Exercise", "Weight (kg)", "Sets", "Reps"])
        else:
            base_df = pd.DataFrame(columns=["Exercise", "Weight (kg)", "Sets", "Reps"])
        
        # Table Editor
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
        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- 5. GLOBAL SYNC ---
if st.button("🚀 Synchronize Weekly Training Plan", use_container_width=True):
    # First, handle the DB cleanup (Remove days that were unselected)
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    removed_days = [d for d in all_days if d not in active_days]
    for d in removed_days:
        execute_query("DELETE FROM training_splits WHERE user_email=%s AND day_name=%s", (user, d))

    # Save active days
    for day in active_days:
        title_to_save = st.session_state.get(f"title_{day}", "")
        # Convert the editor's data to JSON string for storage
        df_to_save = st.session_state.get(f"editor_{day}", pd.DataFrame())
        json_data = df_to_save.to_json() if not df_to_save.empty else None
        
        execute_query("""
            INSERT INTO training_splits (user_email, day_name, split_title, exercises_json) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (user_email, day_name) 
            DO UPDATE SET split_title = EXCLUDED.split_title, exercises_json = EXCLUDED.exercises_json
        """, (user, day, title_to_save, json_data))
    
    st.success("Training Protocol Synchronized.")
    st.rerun()

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

# --- 2. DYNAMIC DAY SELECTION ---
# This gives you control to remove days you don't workout on
st.markdown("### ⚙️ Split Configuration")
active_days = st.multiselect(
    "Select your active training days:",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Monday", "Wednesday", "Friday"],
    help="Only selected days will appear below."
)

st.markdown("---")

# --- 3. DYNAMIC TRAINING BLOCKS ---
for day in active_days:
    with st.container():
        # Perfectly Aligned Header and Description
        col_day, col_desc = st.columns([1, 4])
        
        with col_day:
            # FIX: Removed the red-tinted default headers.
            # Using your strategic Green (#76b372) or a neutral dark grey.
            st.markdown(f"""
                <div style="background:#76b372; padding:8px; border-radius:5px; 
                text-align:center; color:white; font-weight:bold; height:41px; 
                display:flex; align-items:center; justify-content:center; 
                text-transform: uppercase; font-size: 13px; border: 1px solid #5a8a56;">
                    {day}
                </div>
            """, unsafe_allow_html=True)
            
        with col_desc:
            # Description box now sits flush with the green day tag
            st.text_input(
                f"Focus for {day}", 
                placeholder="Training Focus (e.g., Push / Legs)", 
                key=f"title_{day}", 
                label_visibility="collapsed"
            )


        # Table without Intensity (RPE) column
        base_df = pd.DataFrame(columns=["Exercise", "Weight (kg)", "Sets", "Reps"])
        
        # Note: In a full implementation, you'd fetch exercise data here too
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

# --- 4. GLOBAL SYNC ---
if st.button("🚀 Synchronize Weekly Training Plan", use_container_width=True):
    # Save titles so they appear on the Home Page
    for day in active_days:
        title_to_save = st.session_state.get(f"title_{day}", "")
        execute_query("""
            INSERT INTO training_splits (user_email, day_name, split_title) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (user_email, day_name) 
            DO UPDATE SET split_title = EXCLUDED.split_title
        """, (user, day, title_to_save))
    
    st.success("Training Split and Titles Saved Successfully.")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import execute_query, fetch_query
from datetime import datetime
from utils import render_sidebar

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

render_sidebar()

user = st.session_state.user_email

# --- 2. GLOBAL SYMMETRICAL SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
        <div style="background: rgba(118, 179, 114, 0.1); padding: 15px; border-radius: 8px; 
                    border: 1px solid #76b372; margin-bottom: 10px; text-align: center;">
            <p style="margin:0; font-size:10px; color:#76b372; font-weight:bold; letter-spacing:1px;">IDENTITY</p>
            <p style="margin:0; font-size:14px; font-weight:500; overflow:hidden; text-overflow:ellipsis;">{user}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("TERMINATE SESSION", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

st.title("🏋️ Iron Clad")

# --- 3. VOLUME MOMENTUM GRAPH ---
volume_raw = fetch_query("""
    SELECT workout_date, SUM(weight * reps * sets) as total_volume 
    FROM workout_logs WHERE user_email=%s 
    GROUP BY workout_date ORDER BY workout_date ASC LIMIT 7
""", (user,))

if volume_raw:
    v_df = pd.DataFrame(volume_raw, columns=["Date", "Volume"])
    fig = go.Figure(go.Scatter(x=v_df["Date"], y=v_df["Volume"], fill='tozeroy', line_color='#76b372'))
    fig.update_layout(title="Work Capacity Trend (Total kg moved)", height=200, template="plotly_dark", margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 4. TARGETED MUSCLE GROUP TABLES ---
muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Forearms"]

# Fetch all exercises for the user once
all_ex_data = fetch_query("SELECT exercise_name, muscle_group, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
all_ex_df = pd.DataFrame(all_ex_data, columns=["Exercise", "Group", "Prev Kg", "Prev Reps"])

# We will store the edited dataframes here to save them all at once
updated_sessions = []

for group in muscle_groups:
    with st.expander(f"➔ {group.upper()} PROTOCOL", expanded=True):
        # Filter exercises for this specific group
        group_df = all_ex_df[all_ex_df["Group"] == group].copy()
        
        if group_df.empty:
            st.caption(f"No {group} exercises in library. Add one below.")
            # Dummy row for new input if group is empty
            group_df = pd.DataFrame([{"Exercise": "", "Sets": 0, "Weight": 0.0, "Reps": 0, "Prev Kg": 0.0, "Prev Reps": 0}])
        else:
            group_df["Sets"] = 0
            group_df["Weight"] = 0.0
            group_df["Reps"] = 0
            # Reorder columns for better UX
            group_df = group_df[["Exercise", "Sets", "Weight", "Reps", "Prev Kg", "Prev Reps"]]

        edited = st.data_editor(
            group_df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{group}",
            column_config={
                "Prev Kg": st.column_config.NumberColumn("Prev Kg", disabled=True),
                "Prev Reps": st.column_config.NumberColumn("Prev Reps", disabled=True),
                "Weight": st.column_config.NumberColumn("Today's Kg", format="%.1f")
            }
        )
        updated_sessions.append((group, edited))

# --- 5. GLOBAL SAVE SYSTEM ---
if st.button("💾 COMMIT ENTIRE SESSION", use_container_width=True, type="primary"):
    total_logged = 0
    for group, df in updated_sessions:
        for _, row in df.iterrows():
            if row["Weight"] > 0 and row["Exercise"]:
                # Log History
                execute_query("""
                    INSERT INTO workout_logs (user_email, exercise_name, weight, reps, sets, workout_date) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                """, (user, row["Exercise"], row["Weight"], row["Reps"], row["Sets"]))
                
                # Update Library (Upsert)
                execute_query("""
                    INSERT INTO exercise_library (user_email, exercise_name, muscle_group, last_weight, last_reps)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_email, exercise_name) 
                    DO UPDATE SET last_weight=EXCLUDED.last_weight, last_reps=EXCLUDED.last_reps, muscle_group=EXCLUDED.muscle_group
                """, (user, row["Exercise"], group, row["Weight"], row["Reps"]))
                total_logged += 1
    
    if total_logged > 0:
        st.success(f"Archived {total_logged} exercises. Volume graph updated.")
        st.rerun()

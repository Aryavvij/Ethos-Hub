import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user_email
st.title("🏋️ Iron Clad: Performance Lab")

# --- 2. THE SPLIT SELECTOR ---
day_name = datetime.now().strftime("%A")
split_data = fetch_query("SELECT split_title FROM training_splits WHERE user_email=%s AND day_name=%s", (user, day_name))
current_split = split_res[0][0] if split_data else "No Split Assigned"

st.subheader(f"Today's Protocol: {current_split.upper()}")

# --- 3. VOLUME TRACKER (UNIQUE ELEMENT) ---
# Calculates total weight moved (Weight x Reps x Sets)
volume_data = fetch_query("""
    SELECT workout_date, SUM(weight * reps * sets) as total_volume 
    FROM workout_logs 
    WHERE user_email=%s 
    GROUP BY workout_date ORDER BY workout_date DESC LIMIT 7
""", (user,))

if volume_data:
    v_df = pd.DataFrame(volume_data, columns=["Date", "Volume"])
    fig = go.Figure(go.Scatter(x=v_df["Date"], y=v_df["Volume"], fill='tozeroy', line_color='#76b372'))
    fig.update_layout(title="Weekly Volume Load (kg)", height=250, template="plotly_dark", margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- 4. THE EXERCISE LAB (2-COLUMN TABLE STYLE) ---
with st.container(border=True):
    st.subheader("🔥 Execution Log")
    
    # We use a Dynamic Editor for the actual workout
    # Column 1: Exercise Name | Column 2: Weight | Column 3: Sets/Reps
    ex_data = fetch_query("SELECT exercise_name, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
    df = pd.DataFrame(ex_data, columns=["Exercise", "Last Weight", "Last Reps"])
    
    # Adding a 'Today's Weight' and 'Today's Reps' column
    df["Sets"] = 0
    df["Weight"] = 0.0
    df["Reps"] = 0
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Exercise": st.column_config.TextColumn("Exercise", required=True),
            "Weight": st.column_config.NumberColumn("Kg", format="%.1f"),
            "Last Weight": st.column_config.NumberColumn("Prev Kg", disabled=True)
        }
    )

    if st.button("💾 Log Workout & Update PBs", use_container_width=True):
        for _, row in edited_df.iterrows():
            if row["Weight"] > 0:
                # 1. Log to history
                execute_query(
                    "INSERT INTO workout_logs (user_email, exercise_name, weight, reps, sets, workout_date) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)",
                    (user, row["Exercise"], row["Weight"], row["Reps"], row["Sets"])
                )
                # 2. Update Library for "Last Weight" context
                execute_query(
                    "UPDATE exercise_library SET last_weight=%s, last_reps=%s WHERE user_email=%s AND exercise_name=%s",
                    (row["Weight"], row["Reps"], user, row["Exercise"])
                )
        st.success("Volume data committed to the Lab.")
        st.rerun()

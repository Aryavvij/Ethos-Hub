import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🏋️ Iron Clad: Performance Lab")

# --- 2. DYNAMIC SPLIT RECOGNITION ---
day_name = datetime.now().strftime("%A")
# Check what the user is supposed to train today based on the Training Splits table
split_data = fetch_query("SELECT split_title FROM training_splits WHERE user_email=%s AND day_name=%s", (user, day_name))
current_split = split_data[0][0] if split_data else "REST DAY"

st.subheader(f"Today's Protocol: {current_split.upper()}")

# --- 3. VOLUME MOMENTUM (The Unique Factor) ---
# Tracks Total Work Capacity: Weight x Reps x Sets
volume_raw = fetch_query("""
    SELECT workout_date, SUM(weight * reps * sets) as total_volume 
    FROM workout_logs 
    WHERE user_email=%s 
    GROUP BY workout_date ORDER BY workout_date ASC LIMIT 7
""", (user,))

if volume_raw:
    v_df = pd.DataFrame(volume_raw, columns=["Date", "Volume"])
    
    fig = go.Figure(go.Scatter(
        x=v_df["Date"], y=v_df["Volume"], 
        fill='tozeroy', 
        line_color='#76b372',
        fillcolor='rgba(118, 179, 114, 0.2)'
    ))
    fig.update_layout(
        title="Weekly Work Capacity (Total Volume kg)",
        height=250, 
        template="plotly_dark", 
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Log your first workout to see your Volume Momentum.")

# --- 4. THE EXECUTION TABLE (Spreadsheet Style) ---
st.markdown("---")
with st.container(border=True):
    st.subheader("📝 Active Session Log")
    st.caption("Enter today's stats. 'Prev' columns show your last successful session for reference.")

    # Fetch exercise library to provide context for the workout
    lib_data = fetch_query("SELECT exercise_name, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
    
    if not lib_data:
        # Initial state for new users
        df = pd.DataFrame([{"Exercise": "Example: Bench Press", "Sets": 3, "Weight": 60.0, "Reps": 10, "Prev Kg": 0.0, "Prev Reps": 0}])
    else:
        rows = []
        for ex, lw, lr in lib_data:
            rows.append({
                "Exercise": ex,
                "Sets": 0,
                "Weight": 0.0,
                "Reps": 0,
                "Prev Kg": lw if lw else 0.0,
                "Prev Reps": lr if lr else 0
            })
        df = pd.DataFrame(rows)

    # The Grid
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Exercise": st.column_config.TextColumn("Exercise", required=True, width="medium"),
            "Weight": st.column_config.NumberColumn("Today's Kg", format="%.1f", help="Current weight lifted"),
            "Prev Kg": st.column_config.NumberColumn("Prev Kg", disabled=True, format="%.1f"),
            "Prev Reps": st.column_config.NumberColumn("Prev Reps", disabled=True)
        },
        key="workout_editor"
    )

    if st.button("💾 Commit Session to Lab", use_container_width=True):
        valid_entries = 0
        for _, row in edited_df.iterrows():
            ex_name = row["Exercise"].strip()
            if ex_name and row["Weight"] > 0:
                # 1. Log the History
                execute_query("""
                    INSERT INTO workout_logs (user_email, exercise_name, weight, reps, sets, workout_date) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                """, (user, ex_name, row["Weight"], row["Reps"], row["Sets"]))
                
                # 2. Update Library (The context for next time)
                execute_query("""
                    INSERT INTO exercise_library (user_email, exercise_name, last_weight, last_reps)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_email, exercise_name) 
                    DO UPDATE SET last_weight=EXCLUDED.last_weight, last_reps=EXCLUDED.last_reps
                """, (user, ex_name, row["Weight"], row["Reps"]))
                
                valid_entries += 1
        
        if valid_entries > 0:
            st.success(f"Session Committed. {valid_entries} exercises archived.")
            st.rerun()
        else:
            st.error("Please enter at least one exercise with weight > 0.")

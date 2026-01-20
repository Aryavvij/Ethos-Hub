import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import execute_query, fetch_query
from datetime import datetime
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
st.title("🏋️ Iron Clad")
st.caption("Performance Analytics & Progressive Overload Tracking")

# --- CUSTOM CSS FOR ETHOS GREEN BUTTON ---
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #5e8f5b !important;
        border-color: #5e8f5b !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- VOLUME MOMENTUM GRAPH ---
volume_raw = fetch_query("""
    SELECT workout_date, SUM(weight * reps * sets) as total_volume 
    FROM workout_logs WHERE user_email=%s 
    GROUP BY workout_date ORDER BY workout_date ASC LIMIT 7
""", (user,))

if volume_raw:
    v_df = pd.DataFrame(volume_raw, columns=["Date", "Volume"])
    max_vol = v_df["Volume"].max()
    y_limit = max_vol * 1.2 if max_vol > 0 else 1000

    fig = go.Figure(go.Scatter(
        x=v_df["Date"], 
        y=v_df["Volume"], 
        fill='tozeroy', 
        line=dict(color='#76b372', width=3),
        fillcolor='rgba(118, 179, 114, 0.2)',
        mode='lines+markers'
    ))

    fig.update_layout(
        title="<b>Work Capacity Trend (Total Tonnage)</b>",
        height=250, 
        template="plotly_dark", 
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, title="Session History"),
        yaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255,255,255,0.05)",
            title="Total kg Moved",
            range=[0, y_limit],
            rangemode='tozero'
        )
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Log your first session below to initialize the Performance Graph.")

st.markdown("---")

# --- TARGETED MUSCLE GROUP TABLES ---
muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Forearms", "Abs"]

all_ex_data = fetch_query("SELECT exercise_name, muscle_group, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
all_ex_df = pd.DataFrame(all_ex_data, columns=["Exercise", "Group", "Prev Kg", "Prev Reps"])

updated_sessions = []

for group in muscle_groups:
    with st.expander(f"➔ {group.upper()} PROGRESS", expanded=(group == "Abs")):
        group_df = all_ex_df[all_ex_df["Group"] == group].copy()
        
        if group_df.empty:
            st.caption(f"No {group} exercises found. Add your routine below.")
            group_df = pd.DataFrame([{"Exercise": "", "Sets": 0, "Weight": 0.0, "Reps": 0, "Prev Kg": 0.0, "Prev Reps": 0}])
        else:
            group_df["Sets"] = 0
            group_df["Weight"] = 0.0
            group_df["Reps"] = 0
            group_df = group_df[["Exercise", "Sets", "Weight", "Reps", "Prev Kg", "Prev Reps"]]

        edited = st.data_editor(
            group_df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{group}",
            column_config={
                "Prev Kg": st.column_config.NumberColumn("Prev Kg", disabled=True, format="%.1f"),
                "Prev Reps": st.column_config.NumberColumn("Prev Reps", disabled=True),
                "Weight": st.column_config.NumberColumn("Today's Kg", format="%.1f", min_value=0.0),
                "Sets": st.column_config.NumberColumn("Sets", min_value=0),
                "Reps": st.column_config.NumberColumn("Reps", min_value=0)
            }
        )
        updated_sessions.append((group, edited))

# --- DATA SYNCHRONIZATION ---
if st.button("💾 COMMIT ENTIRE SESSION", use_container_width=True, type="primary"):
    total_logged = 0
    for group, df in updated_sessions:
        for _, row in df.iterrows():
            if row["Exercise"] and (row["Weight"] > 0 or row["Reps"] > 0):
                execute_query("""
                    INSERT INTO workout_logs (user_email, exercise_name, weight, reps, sets, workout_date) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                """, (user, row["Exercise"], row["Weight"], row["Reps"], row["Sets"]))
                
                execute_query("""
                    INSERT INTO exercise_library (user_email, exercise_name, muscle_group, last_weight, last_reps)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_email, exercise_name) 
                    DO UPDATE SET last_weight=EXCLUDED.last_weight, last_reps=EXCLUDED.last_reps, muscle_group=EXCLUDED.muscle_group
                """, (user, row["Exercise"], group, row["Weight"], row["Reps"]))
                total_logged += 1
    
    if total_logged > 0:
        st.success(f"Archived {total_logged} exercises. Performance data updated.")
        st.rerun()

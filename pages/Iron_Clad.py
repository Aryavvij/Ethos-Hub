import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
st.title("Iron Clad")
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

# --- GLOBAL OVERVIEW: STACKED STRENGTH EVOLUTION ---
global_evolution = fetch_query("""
    SELECT 
        DATE_TRUNC('month', l.workout_date) as period, 
        ex.muscle_group, 
        SUM(l.weight * l.reps * l.sets) as total_strength
    FROM workout_logs l
    JOIN exercise_library ex ON l.exercise_name = ex.exercise_name
    WHERE l.user_email=%s
    GROUP BY 1, 2 
    ORDER BY 1 ASC
""", (user,))

if global_evolution:
    df_evo = pd.DataFrame(global_evolution, columns=["Period", "Muscle Group", "Strength"])
    
    fig_evo = px.area(
        df_evo, 
        x="Period", 
        y="Strength", 
        color="Muscle Group",
        title="<b>Total Strength Evolution (Monthly Tonnage)</b>",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        height=400
    )
    fig_evo.update_layout(margin=dict(l=10, r=10, t=40, b=10), xaxis_title=None, yaxis_title="kg Moved")
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("Log your first session below to initialize the Evolution Graph.")

st.markdown("---")

# --- TARGETED MUSCLE GROUP TABLES ---
muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Forearms", "Abs"]

all_ex_data = fetch_query("SELECT exercise_name, muscle_group, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
all_ex_df = pd.DataFrame(all_ex_data, columns=["Exercise", "Group", "Prev Kg", "Prev Reps"])

updated_sessions = []

for group in muscle_groups:
    with st.expander(f"➔ {group.upper()} PROGRESS", expanded=(group == "Abs")):
        
        # --- MULTI-LINE EXERCISE PROGRESS CHART ---
        ex_history = fetch_query("""
            SELECT l.workout_date, l.exercise_name, SUM(l.weight * l.reps * l.sets) as total_tonnage
            FROM workout_logs l
            JOIN exercise_library ex ON l.exercise_name = ex.exercise_name
            WHERE l.user_email=%s AND ex.muscle_group=%s
            GROUP BY 1, 2 ORDER BY 1 ASC
        """, (user, group))

        if ex_history:
            h_df = pd.DataFrame(ex_history, columns=["Date", "Exercise", "Total Tonnage"])
            fig_h = px.line(
                h_df, x="Date", y="Total Tonnage", color="Exercise",
                title=f"{group} Work Capacity (Tonnage per Exercise)",
                template="plotly_dark", height=250
            )
            fig_h.update_layout(
                margin=dict(l=0, r=0, t=30, b=0), 
                xaxis_title=None, 
                yaxis_title="Total kg",
                showlegend=True
            )
            fig_h.update_traces(line_width=2, mode='lines+markers', line_shape='spline')
            st.plotly_chart(fig_h, use_container_width=True)

        # --- DATA EDITOR TABLE ---
        group_df = all_ex_df[all_ex_df["Group"] == group].copy()
        
        if group_df.empty:
            st.caption(f"No {group} exercises found. Add your routine below.")
            group_df = pd.DataFrame([{"Exercise": "", "Sets": 0, "Weight": 0.0, "Reps": 0, "Prev Kg": 0.0, "Prev Reps": 0}])
        else:
            group_df = group_df.reset_index(drop=True)
            group_df["Sets"] = 0
            group_df["Weight"] = 0.0
            group_df["Reps"] = 0
            group_df = group_df[["Exercise", "Sets", "Weight", "Reps", "Prev Kg", "Prev Reps"]]

        edited = st.data_editor(
            group_df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
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

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
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
st.title("Iron Clad")
st.caption("Performance Analytics & Progressive Overload Tracking")

# --- CUSTOM CSS ---
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

# --- GLOBAL OVERVIEW: STRENGTH POTENTIAL EVOLUTION (STACKED AREA) ---
global_strength_evo = fetch_query("""
    WITH exercise_strength AS (
        SELECT 
            DATE_TRUNC('month', l.workout_date) as period, 
            ex.muscle_group, 
            l.exercise_name,
            MAX(l.weight * (1 + l.reps / 30.0)) as max_e1rm
        FROM workout_logs l
        JOIN exercise_library ex ON l.exercise_name = ex.exercise_name
        WHERE l.user_email=%s AND l.reps > 0
        GROUP BY 1, 2, 3
    )
    SELECT period, muscle_group, SUM(max_e1rm) as total_muscle_strength
    FROM exercise_strength
    GROUP BY 1, 2 
    ORDER BY 1 ASC
""", (user,))

if global_strength_evo:
    df_strength = pd.DataFrame(global_strength_evo, columns=["Period", "Muscle Group", "Strength Score"])
    
    fig_strength = px.area(
        df_strength, 
        x="Period", 
        y="Strength Score", 
        color="Muscle Group",
        title="<b>Total Strength Potential (Monthly 1RM Evolution)</b>",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        height=450
    )

    fig_strength.update_layout(
        xaxis_title=None,
        yaxis_title="Combined Estimated 1RM (kg)",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    st.plotly_chart(fig_strength, use_container_width=True)
else:
    st.info("Log your sessions to visualize your long-term strength evolution.")

st.markdown("---")

# --- TARGETED MUSCLE GROUP TABLES ---
muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Forearms", "Abs"]

all_ex_data = fetch_query("SELECT exercise_name, muscle_group, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
all_ex_df = pd.DataFrame(all_ex_data, columns=["Exercise", "Group", "Prev Kg", "Prev Reps"])

updated_sessions = []

for group in muscle_groups:
    with st.expander(f"➔ {group.upper()} PROGRESS", expanded=False):
        
        # --- MULTI-LINE EXERCISE PROGRESS CHART (EPLEY 1RM) ---
        ex_history = fetch_query("""
            SELECT 
                l.workout_date, 
                l.exercise_name, 
                MAX(l.weight * (1 + l.reps / 30.0)) as estimated_1rm
            FROM workout_logs l
            JOIN exercise_library ex ON l.exercise_name = ex.exercise_name
            WHERE l.user_email=%s AND ex.muscle_group=%s AND l.reps > 0
            GROUP BY 1, 2 ORDER BY 1 ASC
        """, (user, group))

        if ex_history:
            h_df = pd.DataFrame(ex_history, columns=["Date", "Exercise", "Strength Index"])
            fig_h = px.line(
                h_df, x="Date", y="Strength Index", color="Exercise",
                title=f"{group} Strength Index (Max 1RM Trend)",
                template="plotly_dark", height=250
            )
            fig_h.update_layout(
                margin=dict(l=0, r=0, t=30, b=0), 
                xaxis_title=None, 
                yaxis_title="Est. Max (kg)",
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
if st.button("COMMIT ENTIRE SESSION", use_container_width=True, type="primary"):
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

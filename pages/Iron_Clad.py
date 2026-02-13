import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime, timedelta
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
today = datetime.now().date()
current_week = today - timedelta(days=today.weekday())
st.title("Iron Clad")
st.caption("Performance Analytics & Progressive Overload Tracking")

st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL OVERVIEW: STRENGTH EVOLUTION (STACKED AREA) ---
global_strength_evo = fetch_query("""
    SELECT week_start, muscle_group, volume_sq 
    FROM muscle_progress 
    WHERE user_email=%s 
    ORDER BY week_start ASC
""", (user,))

if global_strength_evo:
    df_strength = pd.DataFrame(global_strength_evo, columns=["Week", "Muscle Group", "Strength Score"])
    
    fig_strength = px.area(
        df_strength, x="Week", y="Strength Score", color="Muscle Group",
        title="<b>Total Strength Potential (Weekly Evolution)</b>",
        template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel,
        height=450
    )
    fig_strength.update_layout(xaxis_title=None, yaxis_title="Combined Strength Score", hovermode="x unified")
    st.plotly_chart(fig_strength, use_container_width=True)
else:
    st.info("Log your sessions to visualize your long-term strength evolution.")

st.markdown("---")

# --- TARGETED MUSCLE GROUP TABLES (THE ORIGINAL UI) ---
muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps", "Forearms", "Abs"]

all_ex_data = fetch_query("SELECT exercise_name, muscle_group, last_weight, last_reps FROM exercise_library WHERE user_email=%s", (user,))
all_ex_df = pd.DataFrame(all_ex_data, columns=["Exercise", "Group", "Prev Kg", "Prev Reps"])

updated_sessions = []

for group in muscle_groups:
    with st.expander(f"➔ {group.upper()} PROGRESS", expanded=False):
        
        # --- INDIVIDUAL LINE CHART FOR EXERCISE ---
        ex_history = fetch_query("""
            SELECT l.workout_date, l.exercise_name, MAX(l.weight * (1 + l.reps / 30.0)) as strength_score
            FROM workout_logs l
            JOIN exercise_library ex ON l.exercise_name = ex.exercise_name
            WHERE l.user_email=%s AND ex.muscle_group=%s AND l.reps > 0
            GROUP BY 1, 2 ORDER BY 1 ASC
        """, (user, group))

        if ex_history:
            h_df = pd.DataFrame(ex_history, columns=["Date", "Exercise", "Score"])
            fig_h = px.line(h_df, x="Date", y="Score", color="Exercise", template="plotly_dark", height=250)
            st.plotly_chart(fig_h, use_container_width=True)

        # --- DATA EDITOR TABLE (ORIGINAL FORMAT) ---
        group_df = all_ex_df[all_ex_df["Group"] == group].copy()
        if group_df.empty:
            group_df = pd.DataFrame([{"Exercise": "", "Sets": 0, "Weight": 0.0, "Reps": 0, "Prev Kg": 0.0, "Prev Reps": 0}])
        else:
            group_df = group_df.reset_index(drop=True)
            group_df["Sets"], group_df["Weight"], group_df["Reps"] = 0, 0.0, 0
            group_df = group_df[["Exercise", "Sets", "Weight", "Reps", "Prev Kg", "Prev Reps"]]

        edited = st.data_editor(group_df, use_container_width=True, num_rows="dynamic", hide_index=True, key=f"editor_{group}")
        updated_sessions.append((group, edited))

# --- DATA SYNCHRONIZATION ---
if st.button("COMMIT ENTIRE SESSION", use_container_width=True, type="primary"):
    total_logged = 0
    
    for group, df in updated_sessions:
        group_weekly_scores = []
        
        for _, row in df.iterrows():
            if row["Exercise"] and (row["Weight"] > 0 or row["Reps"] > 0):
                execute_query("""
                    INSERT INTO workout_logs (user_email, exercise_name, weight, reps, sets, workout_date) 
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
                """, (user, row["Exercise"], row["Weight"], row["Reps"], row["Sets"]))
                
                execute_query("""
                    INSERT INTO exercise_library (user_email, exercise_name, muscle_group, last_weight, last_reps)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_email, exercise_name) DO UPDATE SET last_weight=EXCLUDED.last_weight, last_reps=EXCLUDED.last_reps
                """, (user, row["Exercise"], group, row["Weight"], row["Reps"]))
                
                group_weekly_scores.append(row["Weight"] * (1 + row["Reps"] / 30.0))
                total_logged += 1
        
        if group_weekly_scores:
            avg_group_score = sum(group_weekly_scores) / len(group_weekly_scores)
            existing = fetch_query("SELECT id, volume_sq, frequency FROM muscle_progress WHERE user_email=%s AND muscle_group=%s AND week_start=%s", (user, group, current_week))
            
            if existing:
                row_id, old_score, freq = existing[0]
                final_score = (old_score + avg_group_score) / 2
                execute_query("UPDATE muscle_progress SET volume_sq=%s, frequency=%s WHERE id=%s", (final_score, freq + 1, row_id))
            else:
                execute_query("INSERT INTO muscle_progress (user_email, muscle_group, week_start, volume_sq, frequency) VALUES (%s, %s, %s, %s, 1)", (user, group, current_week, avg_group_score))

    if total_logged > 0:
        st.success(f"Archived {total_logged} exercises and updated Weekly Strength Evolution.")
        st.rerun()

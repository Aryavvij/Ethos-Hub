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
muscle_groups = ["CHEST", "BACK", "LEGS", "SHOULDERS", "ARMS", "ABS"]

st.title("IRON CLAD")
st.caption(f"Weekly Performance Analytics | Cycle: {current_week.strftime('%d %b')}")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
        font-weight: bold;
    }
    .stExpander {
        border: 1px solid rgba(118, 179, 114, 0.2) !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. THE GLOBAL STRENGTH EVOLUTION (STACKED) ---
st.subheader("Total Strength Evolution")

raw_progress = fetch_query("""
    SELECT week_start, muscle_group, volume_sq 
    FROM muscle_progress 
    WHERE user_email=%s 
    ORDER BY week_start ASC
""", (user,))

if raw_progress:
    df_p = pd.DataFrame(raw_progress, columns=["Week", "Muscle Group", "Strength Score"])
    fig_area = px.area(
        df_p, x="Week", y="Strength Score", color="Muscle Group",
        template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel,
        height=400
    )
    fig_area.update_layout(margin=dict(l=10, r=10, t=20, b=10), xaxis_title=None, yaxis_title="Combined Strength Score", hovermode="x unified")
    st.plotly_chart(fig_area, use_container_width=True)

st.markdown("---")

# --- 2. INDIVIDUAL MUSCLE LOGGING & TRENDS ---
st.subheader("Individual Muscle Groups")

for muscle in muscle_groups:
    with st.expander(f"➔ {muscle} PERFORMANCE LOG & TREND", expanded=False):
        # --- PART A: LOGGING FOR THIS MUSCLE ---
        st.write(f"**Log {muscle} Session**")
        c1, c2, c3 = st.columns([2, 2, 1])
        weight = c1.number_input(f"Weight (kg)", min_value=0.0, step=2.5, key=f"w_{muscle}")
        reps = c2.number_input(f"Reps", min_value=0, step=1, key=f"r_{muscle}")
        
        if c3.button("COMMIT", key=f"btn_{muscle}", use_container_width=True, type="primary"):
            if weight > 0 and reps > 0:
                current_score = weight * (1 + reps / 30.0)
                
                existing = fetch_query("""
                    SELECT id, volume_sq, frequency FROM muscle_progress 
                    WHERE user_email=%s AND muscle_group=%s AND week_start=%s
                """, (user, muscle, current_week))
                
                if existing:
                    row_id, old_score, freq = existing[0]
                    avg_score = (old_score + current_score) / 2
                    execute_query("UPDATE muscle_progress SET volume_sq=%s, frequency=%s WHERE id=%s", (avg_score, freq + 1, row_id))
                    st.success("Average adjusted.")
                else:
                    execute_query("INSERT INTO muscle_progress (user_email, muscle_group, week_start, volume_sq, frequency) VALUES (%s, %s, %s, %s, 1)", 
                                  (user, muscle, current_week, current_score))
                    st.success("Session archived.")
                st.rerun()

        # --- PART B: INDIVIDUAL LINE CHART FOR THIS MUSCLE ---
        if raw_progress:
            muscle_df = df_p[df_p["Muscle Group"] == muscle]
            if not muscle_df.empty:
                st.write("---")
                fig_line = px.line(
                    muscle_df, x="Week", y="Strength Score",
                    title=f"{muscle} Strength Trend",
                    template="plotly_dark", markers=True
                )
                fig_line.update_traces(line_color="#76b372", line_width=3, marker=dict(size=8))
                fig_line.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_line, use_container_width=True)
                
                if len(muscle_df) > 1:
                    curr = muscle_df.iloc[-1]["Strength Score"]
                    prev = muscle_df.iloc[-2]["Strength Score"]
                    st.metric("Current Strength Score", f"{curr:.1f}", delta=f"{curr - prev:+.1f}")

# --- 3. DATA FEED ---
with st.expander("VIEW RAW PERFORMANCE HISTORY"):
    if raw_progress:
        st.dataframe(
            pd.DataFrame(raw_progress, columns=["Week", "Muscle", "Score"]).sort_values("Week", ascending=False),
            use_container_width=True, hide_index=True
        )

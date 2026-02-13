import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime, timedelta
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Iron Clad", page_icon="🏋️")

# --- GATEKEEPER ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
today = datetime.now().date()
current_week = today - timedelta(days=today.weekday())
muscle_groups = ["CHEST", "BACK", "LEGS", "SHOULDERS", "ARMS", "ABS"]

st.title("IRONCLAD")
st.caption(f"Weekly Performance Analytics | Cycle: {current_week.strftime('%d %b')}")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
        height: 3em;
        font-weight: bold;
        border-radius: 8px;
    }
    [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(118, 179, 114, 0.1);
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. THE GLOBAL STACKED EVOLUTION ---
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
        df_p, 
        x="Week", 
        y="Strength Score", 
        color="Muscle Group",
        template="plotly_dark", 
        color_discrete_sequence=px.colors.qualitative.Pastel,
        height=400
    )
    fig_area.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title=None,
        yaxis_title="Combined Strength Score",
        hovermode="x unified"
    )
    st.plotly_chart(fig_area, use_container_width=True)
else:
    st.info("Log your first session below to begin visualizing your strength evolution.")

st.markdown("---")

# --- 2. LOGGING SYSTEM ---
st.subheader("Weekly Performance Log")
st.caption("Enter your best set details. If logged twice a week, the average performance is tracked.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    selected_muscle = c1.selectbox("Muscle Group", muscle_groups)
    weight = c2.number_input("Weight (kg)", min_value=0.0, step=2.5)
    reps = c3.number_input("Reps", min_value=0, step=1)

    if st.button("COMMIT PERFORMANCE DATA", use_container_width=True, type="primary"):
        if weight > 0 and reps > 0:
            current_score = weight * (1 + reps / 30.0)
            
            existing = fetch_query("""
                SELECT id, volume_sq, frequency 
                FROM muscle_progress 
                WHERE user_email=%s AND muscle_group=%s AND week_start=%s
            """, (user, selected_muscle, current_week))
            
            if existing:
                row_id, old_score, freq = existing[0]
                avg_score = (old_score + current_score) / 2
                execute_query("""
                    UPDATE muscle_progress SET volume_sq=%s, frequency=%s WHERE id=%s
                """, (avg_score, freq + 1, row_id))
                st.success(f"Session {freq+1} archived. Weekly average adjusted.")
            else:
                execute_query("""
                    INSERT INTO muscle_progress (user_email, muscle_group, week_start, volume_sq, frequency)
                    VALUES (%s, %s, %s, %s, 1)
                """, (user, selected_muscle, current_week, current_score))
                st.success(f"First {selected_muscle} session of the week archived.")
            
            st.rerun()
        else:
            st.warning("Please enter weight and reps to archive data.")

st.markdown("---")

# --- 3. INDIVIDUAL MUSCLE TRENDS ---
st.subheader("Individual Muscle Trends")

if raw_progress:
    df_p = pd.DataFrame(raw_progress, columns=["Week", "Muscle Group", "Strength Score"])
    
    for muscle in muscle_groups:
        muscle_df = df_p[df_p["Muscle Group"] == muscle]
        
        if not muscle_df.empty:
            with st.expander(f"📈 {muscle} PROGRESSION DETAILS"):
                fig_line = px.line(
                    muscle_df, 
                    x="Week", 
                    y="Strength Score",
                    title=f"{muscle} Strength Trend",
                    template="plotly_dark", 
                    markers=True
                )
                fig_line.update_traces(line_color="#76b372", line_width=3, marker=dict(size=8))
                fig_line.update_layout(
                    height=300, 
                    margin=dict(l=10, r=10, t=40, b=10),
                    yaxis_title="Strength Score",
                    xaxis_title=None
                )
                st.plotly_chart(fig_line, use_container_width=True)
                
                if len(muscle_df) > 1:
                    current_val = muscle_df.iloc[-1]["Strength Score"]
                    prev_val = muscle_df.iloc[-2]["Strength Score"]
                    delta = current_val - prev_val
                    st.metric(
                        label=f"Current {muscle} Score", 
                        value=f"{current_val:.1f}", 
                        delta=f"{delta:+.1f}"
                    )
else:
    st.caption("Individual charts will appear once sessions are logged.")

# --- 4. DATA FEED ---
with st.expander("VIEW RAW PERFORMANCE HISTORY"):
    if raw_progress:
        st.dataframe(
            pd.DataFrame(raw_progress, columns=["Week", "Muscle", "Score"]).sort_values("Week", ascending=False),
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.write("No performance logs found.")

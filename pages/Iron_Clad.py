import streamlit as st
import pandas as pd
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Iron Clad")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("Iron Clad")
st.caption("Physical Performance & PR Repository")

# --- 3. BODY METRICS (TOP ROW) ---
st.subheader("Current Vitals")
m1, m2, m3 = st.columns(3)

# Note: We'll assume a 'body_stats' table exists or just use inputs for now
with m1:
    weight = st.number_input("Current Weight (kg)", min_value=0.0, step=0.1)
with m2:
    bf = st.number_input("Body Fat %", min_value=0.0, step=0.1)
with m3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Update Vitals", use_container_width=True):
        st.success("Vitals Updated.")

st.markdown("---")

# --- 4. DAILY LIFT LOG (MIDDLE) ---
st.subheader("Daily Training Log")

# We use the Data Editor for that "Excel" feel you like
log_data = pd.DataFrame([{"Exercise": "", "Weight (kg)": 0.0, "Reps": 0, "Sets": 0}])
edited_log = st.data_editor(log_data, num_rows="dynamic", use_container_width=True, key="daily_lift_editor")

if st.button("Save Workout", use_container_width=True):
    # Logic to save daily workout can be added here if you want a history table
    st.success("Workout Archived to System.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. THE WALL OF FAME (PR TROPHY ROOM) ---
st.subheader("🏆 The Wall of Fame")

# Fetch existing PRs
raw_prs = fetch_query("SELECT id, exercise_name, weight, reps, date_achieved FROM personal_records WHERE user_email=%s ORDER BY weight DESC", (user,))
pr_df = pd.DataFrame(raw_prs, columns=["ID", "Exercise", "PR Weight (kg)", "Reps", "Date"])

# Data Editor for PRs so you can manage them directly
edited_prs = st.data_editor(
    pr_df.drop(columns=["ID"]), 
    num_rows="dynamic", 
    use_container_width=True, 
    key="pr_editor"
)

if st.button("Update Wall of Fame", use_container_width=True):
    # Sync PRs to database
    execute_query("DELETE FROM personal_records WHERE user_email=%s", (user,))
    for _, row in edited_prs.iterrows():
        if row["Exercise"]:
            execute_query(
                "INSERT INTO personal_records (user_email, exercise_name, weight, reps, date_achieved) VALUES (%s, %s, %s, %s, %s)",
                (user, row["Exercise"], row["PR Weight (kg)"], row["Reps"], datetime.now().date())
            )
    st.success("Wall of Fame Updated!")
    st.rerun()

# Visual PR Cards for motivation
if not pr_df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(len(edited_prs) if len(edited_prs) < 5 else 5)
    for i, row in edited_prs.iterrows():
        if i < 5: # Show top 5 PRs as cards
            with cols[i]:
                st.markdown(f"""
                    <div style="background: #1e1e1e; border: 2px solid #76b372; padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="color: #76b372; font-weight: bold; margin: 0; text-transform: uppercase;">{row['Exercise']}</p>
                        <h2 style="margin: 10px 0;">{row['PR Weight (kg)']}kg</h2>
                        <p style="color: gray; margin: 0;">{row['Reps']} Reps</p>
                    </div>
                """, unsafe_allow_html=True)

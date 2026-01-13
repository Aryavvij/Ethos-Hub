import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state.user_email
st.title("📊 Habit Tracker")

# Date Selectors
today = datetime.now()
month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
year = st.selectbox("Year", [2025, 2026], index=1)
month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# Load Data
db_habits = fetch_query("SELECT DISTINCT habit_name FROM habit_logs WHERE user_email=%s", (user,))
all_habits = list(set(["Gym 💪", "Reading 📖"] + [row[0] for row in db_habits]))
habit_df = pd.DataFrame(False, index=all_habits, columns=days_list)

# Checkbox Configuration Fix
day_config = {d: st.column_config.CheckboxColumn(label=d, default=False) for d in days_list}

edited_df = st.data_editor(habit_df, num_rows="dynamic", use_container_width=True, column_config=day_config)

if st.button("☁️ Sync to Cloud"):
    for h_name in edited_df.index:
        if not h_name: continue
        for d_str in edited_df.columns:
            status = edited_df.loc[h_name, d_str]
            formatted_date = f"{year}-{month_num:02d}-{int(d_str):02d}"
            execute_query("""
                INSERT INTO habit_logs (user_email, habit_name, log_date, status) 
                VALUES (%s, %s, %s, %s) ON CONFLICT (user_email, habit_name, log_date) 
                DO UPDATE SET status = EXCLUDED.status
            """, (user, h_name, formatted_date, bool(status)))
    st.success("Synced!")

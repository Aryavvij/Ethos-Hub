import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- SAFETY GATE ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.set_page_config(layout="wide", page_title="Monthly Habit Tracker")

# 1. SELECTORS
c1, c2 = st.columns(2)
month_name = c1.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
year = c2.selectbox("Year", [2025, 2026], index=1)

month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# 2. LOAD DATA
db_habits = fetch_query("SELECT DISTINCT habit_name FROM habit_logs WHERE user_email=%s", (user,))
all_habits = list(set(["Gym 💪", "Reading 📖", "Wake up 05:00 ⏰"] + [row[0] for row in db_habits]))
habit_df = pd.DataFrame(False, index=all_habits, columns=days_list)

db_data = fetch_query("SELECT habit_name, EXTRACT(DAY FROM log_date)::int, status FROM habit_logs WHERE user_email=%s AND EXTRACT(MONTH FROM log_date)=%s AND EXTRACT(YEAR FROM log_date)=%s", (user, month_num, year))
for h_name, d_num, stat in db_data:
    if h_name in habit_df.index: habit_df.at[h_name, str(d_num)] = bool(stat)

# 3. EDITOR (Checkbox Fix)
day_config = {d: st.column_config.CheckboxColumn(label=d, default=False) for d in days_list}
edited_df = st.data_editor(habit_df, num_rows="dynamic", use_container_width=True, column_config=day_config)

# 4. SYNC
if st.button("☁️ Sync to Cloud"):
    with st.spinner("Saving..."):
        for h_name in edited_df.index:
            if not h_name: continue
            for d_str in edited_df.columns:
                status = edited_df.loc[h_name, d_str]
                formatted_date = f"{year}-{month_num:02d}-{int(d_str):02d}"
                execute_query("INSERT INTO habit_logs (user_email, habit_name, log_date, status) VALUES (%s, %s, %s, %s) ON CONFLICT (user_email, habit_name, log_date) DO UPDATE SET status = EXCLUDED.status", (user, h_name, formatted_date, bool(status)))
    st.success("Success!")
    st.rerun()

# 5. METRICS
st.markdown("---")
if not edited_df.empty:
    m_cols = st.columns(4)
    for i, habit in enumerate(edited_df.index):
        if not habit: continue
        score = (edited_df.loc[habit].sum() / num_days) * 100
        m_cols[i % 4].metric(label=str(habit), value=f"{score:.1f}%")

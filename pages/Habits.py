import streamlit as st
import pandas as pd
import calendar
from database import execute_query, fetch_query

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Habit Tracker")

c1, c2 = st.columns(2)
with c1:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:])
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028, 2029, 2030])

month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# fetch habit logs from cloud for this month
user = st.session_state.user_email
# habit_name, log_date, status
db_data = fetch_query("""SELECT habit_name, EXTRACT(DAY FROM log_date)::int, status 
                         FROM habits WHERE user_email=%s AND EXTRACT(MONTH FROM log_date)=%s 
                         AND EXTRACT(YEAR FROM log_date)=%s""", (user, month_num, year))

# setup the dataframe
default_habits = ["Wake up 05:00 ⏰", "Gym 💪", "Reading 📖"]
habit_df = pd.DataFrame(False, index=default_habits, columns=days_list)

# fill dataframe with cloud data
for h_name, d_num, stat in db_data:
    if h_name in habit_df.index and str(d_num) in habit_df.columns:
        habit_df.at[h_name, str(d_num)] = stat

edited_df = st.data_editor(habit_df, num_rows="dynamic", use_container_width=True)

if st.button("☁️ Save to Cloud"):
    for h_name in edited_df.index:
        for d_str in edited_df.columns:
            status = edited_df.loc[h_name, d_str]
            log_date = f"{year}-{month_num}-{int(d_str):02d}"
            # upsert logic (insert or update if exists)
            execute_query("""INSERT INTO habits (user_email, habit_name, log_date, status) 
                             VALUES (%s, %s, %s, %s)
                             ON CONFLICT (user_email, habit_name, log_date) 
                             DO UPDATE SET status = EXCLUDED.status""", 
                          (user, h_name, log_date, bool(status)))
    st.success("Habits synced with Supabase!")

st.markdown("---")
st.subheader("Success Rates")
cols = st.columns(4)
for i, habit in enumerate(edited_df.index):
    success_rate = (edited_df.loc[habit].sum() / num_days) * 100
    cols[i % 4].metric(str(habit), f"{success_rate:.1f}%")

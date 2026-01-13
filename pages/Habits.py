import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- AUTH CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

# --- SIDEBAR LOGOUT ---
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("📊 Monthly Habit Tracker")

user = st.session_state.user_email
today = datetime.now()

# 1. DATE SELECTION
c1, c2 = st.columns(2)
with c1:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028, 2029, 2030], index=1)

month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# 2. DYNAMIC HABIT LOADING
# Fetch every habit name you've ever saved so they don't disappear on logout
db_habits = fetch_query("SELECT DISTINCT habit_name FROM habits WHERE user_email=%s", (user,))
persisted_habits = [row[0] for row in db_habits]

# Combine defaults with your custom ones
default_habits = ["Gym 💪", "Reading 📖", "Wake up 05:00 ⏰"]
all_habits = list(set(default_habits + persisted_habits))

# 3. FETCH COMPLETION DATA
db_data = fetch_query("""
    SELECT habit_name, EXTRACT(DAY FROM log_date)::int, status 
    FROM habits 
    WHERE user_email=%s AND EXTRACT(MONTH FROM log_date)=%s AND EXTRACT(YEAR FROM log_date)=%s
""", (user, month_num, year))

# Initialize the grid (All habits get a full row of boxes)
habit_df = pd.DataFrame(False, index=all_habits, columns=days_list)

for h_name, d_num, stat in db_data:
    if h_name in habit_df.index and str(d_num) in habit_df.columns:
        habit_df.at[h_name, str(d_num)] = bool(stat)

# 4. THE DATA EDITOR (Updated with Checkbox Fix)
st.info("💡 Add new habits in the bottom row. Boxes will appear for the whole month instantly!")

# This specific configuration fixes the "Red Triangle" issue by forcing 
# new rows to use Checkbox columns instead of text
day_config = {
    d: st.column_config.CheckboxColumn(label=d, default=False) 
    for d in days_list
}

edited_df = st.data_editor(
    habit_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config=day_config
)

# 5. SYNC TO CLOUD
if st.button("☁️ Sync to Supabase"):
    with st.spinner("Syncing with cloud..."):
        for h_name in edited_df.index:
            for d_str in edited_df.columns:
                status = edited_df.loc[h_name, d_str]
                # Format date correctly for PostgreSQL (YYYY-MM-DD)
                formatted_date = f"{year}-{month_num:02d}-{int(d_str):02d}"
                
                # UPSERT logic requires the SQL Unique Constraint to be active
                execute_query("""
                    INSERT INTO habits (user_email, habit_name, log_date, status) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_email, habit_name, log_date) 
                    DO UPDATE SET status = EXCLUDED.status
                """, (user, h_name, formatted_date, bool(status)))
    st.success("Sync complete!")
    st.rerun()

# 6. DYNAMIC SUCCESS RATES
st.markdown("---")
st.subheader("Monthly Consistency Score")
if not edited_df.empty:
    # m_cols handles up to 4 metrics per row
    m_cols = st.columns(4) 
    for i, habit in enumerate(edited_df.index):
        # Calculate success rate based on number of ticks
        completed = edited_df.loc[habit].sum()
        score = (completed / num_days) * 100
        with m_cols[i % 4]:
            st.metric(label=str(habit), value=f"{score:.1f}%", delta=f"{int(completed)} days")

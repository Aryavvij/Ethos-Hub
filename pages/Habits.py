import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- SAFETY GATE ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in on the Home page.")
    if st.button("Go to Login"): st.switch_page("Home.py")
    st.stop()

user = st.session_state.user_email

with st.sidebar:
    st.success(f"Logged in: {user}")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.title("📊 Monthly Habit Tracker")

# ... (Date selectors and loading logic here) ...

# --- DATA EDITOR FIX ---
# Force checkboxes for all days to prevent red triangles
day_config = {str(d): st.column_config.CheckboxColumn(label=str(d), default=False) 
              for d in range(1, num_days + 1)}

edited_df = st.data_editor(
    habit_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config=day_config
)

# ... (Sync logic using habit_logs) ...

# 1. DATE SELECTORS
c1, c2 = st.columns(2)
with c1:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)
with c2:
    year = st.selectbox("Year", [2025, 2026, 2027, 2028, 2029, 2030], index=1)

month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# 2. LOAD HABITS & DATA (Updated table name to habit_logs)
# We fetch from habit_logs to avoid the corrupted old table
db_habits = fetch_query("SELECT DISTINCT habit_name FROM habit_logs WHERE user_email=%s", (user,))
persisted_habits = [row[0] for row in db_habits]

# Combine defaults with your custom ones
default_habits = ["Gym 💪", "Reading 📖", "Wake up 05:00 ⏰"]
all_habits = list(set(default_habits + persisted_habits))

# Initialize the grid
habit_df = pd.DataFrame(False, index=all_habits, columns=days_list)

# Fetch completion data from habit_logs
db_data = fetch_query("""
    SELECT habit_name, EXTRACT(DAY FROM log_date)::int, status 
    FROM habit_logs 
    WHERE user_email=%s AND EXTRACT(MONTH FROM log_date)=%s AND EXTRACT(YEAR FROM log_date)=%s
""", (user, month_num, year))

for h_name, d_num, stat in db_data:
    if h_name in habit_df.index and str(d_num) in habit_df.columns:
        habit_df.at[h_name, str(d_num)] = bool(stat)

# 3. DATA EDITOR FIX
st.info("💡 Tip: Add new habits in the bottom row. Boxes will appear for the whole month!")

# This column_config is the "magic" that removes red triangles
day_config = {d: st.column_config.CheckboxColumn(label=d, default=False) for d in days_list}

edited_df = st.data_editor(
    habit_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config=day_config
)

# 4. SYNC LOGIC (Updated table name to habit_logs)
if st.button("☁️ Sync to Supabase"):
    try:
        for h_name in edited_df.index:
            if not h_name: continue
            for d_str in edited_df.columns:
                status = edited_df.loc[h_name, d_str]
                formatted_date = f"{year}-{month_num:02d}-{int(d_str):02d}"
                
                # We use habit_logs (the new clean table)
                execute_query("""
                    INSERT INTO habit_logs (user_email, habit_name, log_date, status) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_email, habit_name, log_date) 
                    DO UPDATE SET status = EXCLUDED.status
                """, (user, h_name, formatted_date, bool(status)))
        st.success("Sync complete!")
        st.rerun()
    except Exception as e:
        st.error(f"Sync failed. Please refresh the page. Error: {e}")

# 5. DYNAMIC METRICS
st.markdown("---")
st.subheader("Monthly Consistency Score")
if not edited_df.empty:
    m_cols = st.columns(4) 
    for i, habit in enumerate(edited_df.index):
        if not habit: continue # Skip unnamed habits
        completed = edited_df.loc[habit].sum()
        score = (completed / num_days) * 100
        with m_cols[i % 4]:
            st.metric(label=str(habit), value=f"{score:.1f}%", delta=f"{int(completed)} days")

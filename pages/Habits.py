import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime
import calendar

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Habit Lab", page_icon="📈")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("📈 Habit Lab")

# --- 2. DATE SELECTORS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]
day_cols = [str(i) for i in range(1, days_in_month + 1)]

# --- 3. DATA ENGINE (STRICT FILTERING) ---
raw_data = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

# Identify unique habits already in DB
unique_habits = sorted(list(set([row[0] for row in raw_data if row[0]])))

# Fallback to defaults ONLY if the DB is completely empty
if not unique_habits:
    unique_habits = ["Coursera Video", "4L Water Intake", "Minimum Sugar", "7.5 Hour Sleep", "Attended Classes", "Book Reading", "Protein Goal", "Gym/Training", "Brushing Twice"]

# Build rows: ONLY for habits that actually exist
rows = []
for h_name in unique_habits:
    row_dict = {"Habit Name": h_name}
    for d in day_cols:
        row_dict[d] = False
    # Map status from DB
    for db_name, db_day, db_status in raw_data:
        if db_name == h_name:
            row_dict[str(db_day)] = bool(db_status)
    rows.append(row_dict)

# Create the clean DF
df = pd.DataFrame(rows, columns=["Habit Name"] + day_cols)

# --- 4. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True, width="medium"),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False, width="small")

    # FIX: We use a dynamic key based on month/year. 
    # This forces Streamlit to refresh the grid and clear "ghost" rows when you change dates.
    editor_key = f"habit_editor_{month_num}_{year}"
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=450, 
        num_rows="dynamic",
        column_config=col_config,
        key=editor_key
    )

    if st.button("💾 Synchronize System", use_container_width=True):
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
        for _, row in edited_df.iterrows():
            h_name = row.get("Habit Name")
            if h_name and str(h_name).strip() != "":
                h_name_clean = str(h_name).strip()
                for day_str in day_cols:
                    if row.get(day_str) == True:
                        execute_query(
                            "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user, h_name_clean, month_num, year, int(day_str), True)
                        )
        st.success("System Synchronized.")
        st.rerun()

# --- 5. PERFORMANCE MATRIX ---
# Only calculate for rows that have a name
valid_df = edited_df[edited_df["Habit Name"].fillna("").str.strip() != ""]
if not valid_df.empty:
    st.markdown("---")
    st.subheader("📊 Performance Matrix")
    total_habits = len(valid_df)
    daily_done = valid_df[day_cols].sum(axis=0).astype(int)
    daily_progress = ((daily_done / total_habits) * 100).round(1)

    stats_df = pd.DataFrame({
        "Progress": [f"{p}%" for p in daily_progress],
        "Done": daily_done.values,
        "Total": [total_habits] * days_in_month
    }).T
    stats_df.columns = day_cols
    st.dataframe(stats_df, use_container_width=True)

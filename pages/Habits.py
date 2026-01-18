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
st.caption("Custom habit tracking & performance analytics.")

# --- 2. DATE SELECTORS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]
day_cols = [str(i) for i in range(1, days_in_month + 1)]

# --- 3. DATA ENGINE (PURE DYNAMIC) ---
# Fetch every unique habit this user has for THIS specific month
raw_data = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

# Identify unique habits from the database results
unique_habits = list(set([row[0] for row in raw_data]))

# Build the DataFrame frame first
# We start with "Habit Name" as a column, not an index, to support dynamic row adding
if not unique_habits:
    # If brand new month, start with one empty row to show checkboxes exist
    df = pd.DataFrame(columns=["Habit Name"] + day_cols)
    new_row = {col: False for col in day_cols}
    new_row["Habit Name"] = ""
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
else:
    df = pd.DataFrame(columns=["Habit Name"] + day_cols)
    for h_name in unique_habits:
        # Initialize row with False
        row_dict = {str(d): False for d in range(1, days_in_month + 1)}
        row_dict["Habit Name"] = h_name
        # Fill in existing True statuses
        for db_name, db_day, db_status in raw_data:
            if db_name == h_name:
                row_dict[str(db_day)] = bool(db_status)
        df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)

# --- 4. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    # We define the column configuration to force checkboxes on ALL numeric day columns
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False)

    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=500, 
        num_rows="dynamic", # Users can add/delete
        column_config=col_config,
        key="habit_editor_dynamic_v7"
    )

    if st.button("💾 Synchronize System", use_container_width=True):
        # 1. Wipe current month for this user
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
        # 2. Re-insert only rows that have a Habit Name
        for _, row in edited_df.iterrows():
            h_name = row["Habit Name"]
            if h_name and str(h_name).strip() != "":
                for day_str in day_cols:
                    if row[day_str] == True:
                        execute_query(
                            "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user, h_name.strip(), month_num, year, int(day_str), True)
                        )
        st.success("Consistency Locked.")
        st.rerun()

st.markdown("---")

# --- 5. PERFORMANCE SUMMARY ---
# Calculate stats only if habits exist
if not edited_df.empty and edited_df["Habit Name"].iloc[0] != "":
    stats_base = edited_df.dropna(subset=["Habit Name"])
    total_habits = len(stats_base)
    
    daily_done = stats_base[day_cols].sum(axis=0).astype(int)
    daily_progress = ((daily_done / total_habits) * 100).round(1)

    stats_df = pd.DataFrame({
        "Progress": [f"{p}%" for p in daily_progress],
        "Done": daily_done.values,
        "Total": [total_habits] * days_in_month
    }).T
    stats_df.columns = day_cols

    st.subheader("📊 Performance Matrix")
    st.dataframe(stats_df, use_container_width=True)

    # Momentum Chart
    chart_data = pd.DataFrame({
        "Day": range(1, days_in_month + 1),
        "Completed": daily_done.values
    })
    fig = px.area(chart_data, x="Day", y="Completed", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

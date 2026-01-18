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

# --- 3. DATA ENGINE (FIXED ROW LOGIC) ---
raw_data = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

unique_habits = sorted(list(set([row[0] for row in raw_data])))

# We build a list of dictionaries first to prevent "Row Multiplication"
rows = []
if not unique_habits:
    # JUST ONE empty row for fresh start
    new_row = {col: False for col in day_cols}
    new_row["Habit Name"] = ""
    rows.append(new_row)
else:
    for h_name in unique_habits:
        row_dict = {str(d): False for d in range(1, days_in_month + 1)}
        row_dict["Habit Name"] = h_name
        # Fill existing completions
        for db_name, db_day, db_status in raw_data:
            if db_name == h_name:
                row_dict[str(db_day)] = bool(db_status)
        rows.append(row_dict)

df = pd.DataFrame(rows)

# --- 4. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    # Configure Columns to force Checkboxes for all days
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True, width="medium"),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False, width="small")

    # num_rows="dynamic" adds the empty row at bottom automatically
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=450, 
        num_rows="dynamic",
        column_config=col_config,
        key="habit_editor_v8"
    )

    if st.button("💾 Synchronize System", use_container_width=True):
        # 1. Clear current month
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
        # 2. Insert rows that have names
        for _, row in edited_df.iterrows():
            h_name = row["Habit Name"]
            if h_name and str(h_name).strip() != "":
                for day_str in day_cols:
                    if row.get(day_str) == True:
                        execute_query(
                            "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user, h_name.strip(), month_num, year, int(day_str), True)
                        )
        st.success("Habit data locked.")
        st.rerun()

st.markdown("---")

# --- 5. PERFORMANCE SUMMARY ---
# Ensure we don't calculate stats on empty/placeholder rows
valid_df = edited_df[edited_df["Habit Name"].str.strip() != ""]

if not valid_df.empty:
    total_habits = len(valid_df)
    daily_done = valid_df[day_cols].sum(axis=0).astype(int)
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
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      yaxis=dict(title="Habits Done", tickmode='linear', dtick=1))
    st.plotly_chart(fig, use_container_width=True)

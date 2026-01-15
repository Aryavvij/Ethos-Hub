import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime, date
import calendar

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Habit Lab", page_icon="📈")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("📈 Monthly Habit Tracker")

# --- 2. DATE SELECTORS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2024, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]

# --- 3. DATA ENGINE ---
# Fetch existing data for current month
raw_habits = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

# Initialize Pivot Table
habit_list = ["Brushing Morning", "Book Reading", "Coursera Video", "7 Hour Sleep", 
              "Minimum Sugar", "Protein Goal", "Brushing Night", "Gym/Training", 
              "Teeth Gel", "Attended Classes", "Bath", "Jogging"]

# Create empty DataFrame for the editor
df = pd.DataFrame(index=habit_list, columns=[str(i) for i in range(1, days_in_month + 1)]).fillna(False)

# Populate with DB data
for h_name, h_day, h_status in raw_habits:
    if h_name in df.index and str(h_day) in df.columns:
        df.at[h_name, str(h_day)] = bool(h_status)

# --- 4. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        height=400,
        key=f"habit_editor_{month_num}_{year}"
    )

    if st.button("☁️ Sync to Cloud", use_container_width=True):
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        for habit, row in edited_df.iterrows():
            for day_col, status in row.items():
                if status:
                    execute_query(
                        "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user, habit, month_num, year, int(day_col), 1)
                    )
        st.success("Consistency Synced.")
        st.rerun()

st.markdown("---")

# --- 5. PERFORMANCE SUMMARY TABLE ---
# Calculate Stats
daily_counts = edited_df.sum(axis=0) # Total habits done per day
total_habits = len(habit_list)

stats_df = pd.DataFrame({
    "Progress": [(count / total_habits) * 100 for count in daily_counts],
    "Done": daily_counts,
    "Not Done": [total_habits - count for count in daily_counts]
}).T
stats_df.columns = [str(i) for i in range(1, days_in_month + 1)]

st.subheader("📊 Performance Statistics")
st.data_editor(
    stats_df,
    use_container_width=True,
    disabled=True,
    column_config={col: st.column_config.NumberColumn(format="%.0f") for col in stats_df.columns}
)

# --- 6. VISUAL MOMENTUM (AREA CHART) ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🌊 Consistency Momentum")

# Prepare Chart Data
chart_data = pd.DataFrame({
    "Day": range(1, days_in_month + 1),
    "Completed Habits": daily_counts.values
})

fig = px.area(
    chart_data, 
    x="Day", 
    y="Completed Habits",
    title=f"Habit Completion Volume - {month_name}",
    color_discrete_sequence=['#76b372']
)

fig.update_layout(
    xaxis=dict(tickmode='linear', tick0=1, dtick=1),
    yaxis=dict(range=[0, total_habits + 1]),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=350,
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

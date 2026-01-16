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
st.caption("Monthly Consistency & Performance Analytics")

# --- 2. DATE SELECTORS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]
day_cols = [str(i) for i in range(1, days_in_month + 1)]

# --- 3. DATA ENGINE ---
raw_habits = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

habit_list = [
    "Brushing Morning", "Book Reading", "Coursera Video", "7 Hour Sleep", 
    "Minimum Sugar", "Protein Goal", "Brushing Night", "Gym/Training", 
    "Teeth Gel", "Attended Classes", "Bath", "Jogging"
]

# Build the main grid
df = pd.DataFrame(index=habit_list, columns=day_cols).fillna(False)
for h_name, h_day, h_status in raw_habits:
    if h_name in df.index and str(h_day) in df.columns:
        df.at[h_name, str(h_day)] = bool(h_status)

# --- 4. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Habit Grid")
    edited_df = st.data_editor(df, use_container_width=True, height=400, key="habit_editor_v5")

    if st.button("💾 Synchronize Habit Lab", use_container_width=True):
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        for habit, row in edited_df.iterrows():
            for day_str, status in row.items():
                if status:
                    # FIX: We pass Python 'True' which SQL recognizes as BOOLEAN
                    execute_query(
                        "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user, habit, month_num, year, int(day_str), True)
                    )
        st.success("Consistency Synced.")
        st.rerun()

st.markdown("---")

# --- 5. PERFORMANCE STATISTICS TABLE (Horizontal 3-Row Table) ---
daily_done = edited_df.sum(axis=0).astype(int)
total_possible = len(habit_list)
daily_progress = ((daily_done / total_possible) * 100).round(0).astype(int)
daily_not_done = total_possible - daily_done

# Creating the horizontal 3-row table
stats_df = pd.DataFrame({
    "Progress": [f"{p}%" for p in daily_progress],
    "Done": daily_done,
    "Not Done": daily_not_done
}).T
stats_df.columns = day_cols

st.subheader("📊 Daily Performance Summary")
# Displaying as a non-editable dataframe for a professional look
st.dataframe(stats_df, use_container_width=True)

# --- 6. VISUAL MOMENTUM CHART ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🌊 Consistency Momentum")

chart_data = pd.DataFrame({
    "Day": range(1, days_in_month + 1),
    "Completed": daily_done.values
})

fig = px.area(
    chart_data, x="Day", y="Completed",
    color_discrete_sequence=['#76b372'],
    template="plotly_dark"
)

fig.update_layout(
    yaxis=dict(title="Habits Done", range=[0, total_possible + 1], gridcolor="rgba(255,255,255,0.05)"),
    xaxis=dict(title="Day of Month", tickmode='linear', dtick=5, gridcolor="rgba(255,255,255,0.05)"),
    height=350,
    margin=dict(l=0, r=0, t=20, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

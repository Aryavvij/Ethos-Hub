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

# --- 2. VERSION CONTROL (FORCES UI TO KILL PHANTOM ROWS) ---
if 'habit_version' not in st.session_state:
    st.session_state.habit_version = 0

# --- 3. DATE SELECTORS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]
day_cols = [str(i) for i in range(1, days_in_month + 1)]

# --- 4. DATA ENGINE (STRICT ROW BUILDING) ---
raw_data = fetch_query(
    "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
    (user, month_num, year)
)

# Pull unique habits from DB
db_habits = sorted(list(set([row[0] for row in raw_data if row[0]])))

# Fallback defaults if month is empty
unique_habits = db_habits if db_habits else ["4L Water Intake", "7.5 Hour Sleep", "Attended Classes", "Book Reading", "Brushing Twice", "Coursera Video", "Gym/Training", "Minimum Sugar", "Protein Goal"]

rows = []
for h_name in unique_habits:
    row_dict = {"Habit Name": h_name}
    for d in day_cols:
        row_dict[d] = False
    for db_name, db_day, db_status in raw_data:
        if db_name == h_name:
            row_dict[str(db_day)] = bool(db_status)
    rows.append(row_dict)

# Build DF - We ensure it starts with NO extra blank rows in the data itself
df = pd.DataFrame(rows, columns=["Habit Name"] + day_cols)

# --- 5. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True, width="medium"),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False, width="small")

    # The Key includes 'habit_version' which we increment to clear ghost rows on sync
    editor_key = f"habit_v{st.session_state.habit_version}_{month_num}_{year}"
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=450, 
        num_rows="dynamic", # Provides exactly one '+' row at the bottom
        column_config=col_config,
        key=editor_key
    )

    if st.button("💾 Synchronize System", use_container_width=True):
        # 1. Clear DB
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
        # 2. Sync named rows
        for _, row in edited_df.iterrows():
            h_name = row.get("Habit Name")
            if h_name and str(h_name).strip() != "":
                h_clean = str(h_name).strip()
                for day_str in day_cols:
                    if row.get(day_str) == True:
                        execute_query(
                            "INSERT INTO habits (user_email, habit_name, month, year, day, status) VALUES (%s, %s, %s, %s, %s, %s)",
                            (user, h_clean, month_num, year, int(day_str), True)
                        )
        
        # 3. Increment version to reset the widget state and kill the 3 empty rows
        st.session_state.habit_version += 1
        st.success("Synchronized. Grid reset.")
        st.rerun()

# --- 6. PERFORMANCE & MOMENTUM (Y-AXIS FIXED) ---
valid_df = edited_df[edited_df["Habit Name"].fillna("").str.strip() != ""]

if not valid_df.empty:
    st.markdown("---")
    
    # 6a. Performance Matrix
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

    # 6b. Momentum Chart (Y-AXIS LOCKED TO TOTAL HABITS)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌊 Consistency Momentum")
    
    chart_data = pd.DataFrame({
        "Day": [int(d) for d in day_cols],
        "Completed": daily_done.values
    })

    fig = px.area(
        chart_data, x="Day", y="Completed",
        color_discrete_sequence=['#76b372'],
        template="plotly_dark"
    )

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # FIXED: Range now locks from 0 to your Total Number of Habits
        yaxis=dict(
            title="Habits Done", 
            range=[0, total_habits], 
            tickmode='linear', 
            dtick=1, 
            gridcolor="rgba(255,255,255,0.05)"
        ),
        xaxis=dict(title="Day of Month", tickmode='linear', dtick=5, gridcolor="rgba(255,255,255,0.05)")
    )

    st.plotly_chart(fig, use_container_width=True)

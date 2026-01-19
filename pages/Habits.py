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

# --- 2. THE HARD RESET LOGIC ---
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

# --- 4. DATA ENGINE (FIXED: SESSION STATE BRIDGE) ---
# Create a unique key for the current month/year
data_key = f"data_{month_num}_{year}_{st.session_state.habit_version}"

if data_key not in st.session_state:
    raw_data = fetch_query(
        "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
        (user, month_num, year)
    )
    db_habits = sorted(list(set([row[0] for row in raw_data if row[0]])))
    
    rows = []
    # If brand new: ONLY ONE single empty row.
    if not db_habits:
        new_row = {"Habit Name": ""}
        for d in day_cols: new_row[d] = False
        rows.append(new_row)
    else:
        for h_name in db_habits:
            row_dict = {"Habit Name": h_name}
            for d in day_cols: row_dict[d] = False
            for db_name, db_day, db_status in raw_data:
                if db_name == h_name:
                    row_dict[str(db_day)] = bool(db_status)
            rows.append(row_dict)
    
    st.session_state[data_key] = pd.DataFrame(rows, columns=["Habit Name"] + day_cols)

# --- 5. MAIN EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True, width="medium"),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False, width="small")

    # Use the session state data as the source
    edited_df = st.data_editor(
        st.session_state[data_key], 
        use_container_width=True, 
        height=400, 
        num_rows="dynamic",
        column_config=col_config,
        key=f"editor_{data_key}"
    )

    if st.button("💾 Synchronize System", use_container_width=True):
        # 1. Update the session state immediately
        st.session_state[data_key] = edited_df
        
        # 2. Wipe DB for this month
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
        # 3. Save from the edited_df
        save_count = 0
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
                save_count += 1
        
        # 4. Bump version to force a clean re-fetch next time and clear phantom rows
        st.session_state.habit_version += 1
        st.success(f"Successfully Synchronized {save_count} habits.")
        st.rerun()

# --- 6. PERFORMANCE & MOMENTUM ---
valid_df = edited_df[edited_df["Habit Name"].fillna("").str.strip() != ""]

if not valid_df.empty:
    st.markdown("---")
    total_habits_count = len(valid_df)
    daily_done = valid_df[day_cols].sum(axis=0).astype(int)
    daily_progress = ((daily_done / total_habits_count) * 100).round(1)

    # Performance Matrix
    stats_df = pd.DataFrame({
        "Progress": [f"{p}%" for p in daily_progress],
        "Done": daily_done.values,
        "Total": [total_habits_count] * days_in_month
    }).T
    stats_df.columns = day_cols
    st.subheader("📊 Performance Matrix")
    st.dataframe(stats_df, use_container_width=True)

    # Momentum Chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌊 Consistency Momentum")
    chart_data = pd.DataFrame({"Day": [int(d) for d in day_cols], "Completed": daily_done.values})
    fig = px.area(chart_data, x="Day", y="Completed", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig.update_layout(
        height=400, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="Habits Done", range=[0, total_habits_count + 0.2], tickmode='linear', dtick=1, gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(title="Day of Month", tickmode='linear', dtick=5, gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime
import calendar
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Habit Lab", page_icon="📈")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
st.title("Habit Lab")

if 'habit_version' not in st.session_state:
    st.session_state.habit_version = 0

# --- DATE FILTERS ---
col_m, col_y = st.columns(2)
with col_m:
    month_name = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
    month_num = list(calendar.month_name).index(month_name)
with col_y:
    year = st.number_input("Year", min_value=2025, max_value=2030, value=datetime.now().year)

days_in_month = calendar.monthrange(year, month_num)[1]
day_cols = [str(i) for i in range(1, days_in_month + 1)]

# --- DATA ENGINE ---
data_key = f"data_{month_num}_{year}_{st.session_state.habit_version}"

if data_key not in st.session_state:
    raw_data = fetch_query(
        "SELECT habit_name, day, status FROM habits WHERE user_email=%s AND month=%s AND year=%s",
        (user, month_num, year)
    )
    db_habits = sorted(list(set([row[0] for row in raw_data if row[0]])))
    
    rows = []
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

# --- HABIT GRID EDITOR ---
with st.container(border=True):
    st.subheader(f"🗓️ {month_name} Grid")
    
    col_config = {
        "Habit Name": st.column_config.TextColumn("Habit Name", required=True, width="medium"),
    }
    for day in day_cols:
        col_config[day] = st.column_config.CheckboxColumn(day, default=False, width="small")

    edited_df = st.data_editor(
        st.session_state[data_key], 
        use_container_width=True, 
        height=400, 
        num_rows="dynamic",
        column_config=col_config,
        key=f"editor_{data_key}"
    )

    if st.button("Synchronize Table", use_container_width=True):
        st.session_state[data_key] = edited_df
        execute_query("DELETE FROM habits WHERE user_email=%s AND month=%s AND year=%s", (user, month_num, year))
        
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
        
        st.session_state.habit_version += 1
        st.success(f"Successfully Synchronized {save_count} habits.")
        st.rerun()

# --- ANALYTICS & MONTHLY PERFORMANCE ---
valid_df = edited_df[edited_df["Habit Name"].fillna("").str.strip() != ""]

if not valid_df.empty:
    total_habits_count = len(valid_df)
    daily_done = valid_df[day_cols].sum(axis=0).astype(int)
    
    st.subheader("Consistency Momentum")
    chart_data = pd.DataFrame({"Day": [int(d) for d in day_cols], "Completed": daily_done.values})
    fig = px.area(chart_data, x="Day", y="Completed", color_discrete_sequence=['#76b372'], template="plotly_dark")
    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="Habits Done", range=[0, total_habits_count + 0.2], tickmode='linear', dtick=1),
        xaxis=dict(title="Day of Month", tickmode='linear', dtick=5)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Monthly Performance Overview")
    
    habit_stats = []
    ethos_green = "#76b372" 

    # UPDATE: Logic for "Till Today" denominator
    today = datetime.now()
    if year == today.year and month_num == today.month:
        denominator = today.day
    else:
        denominator = days_in_month

    for i, (_, row) in enumerate(valid_df.iterrows(), start=1):
        name = row["Habit Name"]
        if name:
            done_count = sum(1 for d in day_cols if row[d] == True)
            # Calculate % based on elapsed days (denominator)
            pct = (done_count / denominator) * 100
            habit_stats.append({
                "#": str(i),
                "Habit": name,
                "Days Completed": str(done_count),
                "Consistency": pct
            })

    if habit_stats:
        cols = st.columns(3)
        for idx, stat in enumerate(habit_stats):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div style="border: none; border-radius: 10px; padding: 20px; 
                                background: rgba(255,255,255,0.05); margin-bottom: 15px;">
                        <p style="margin:0; font-size:11px; color:gray; text-transform:uppercase; letter-spacing:1px;">Habit #{stat["#"]}</p>
                        <h3 style="margin:5px 0 15px 0; color:white; font-size:18px;">{stat["Habit"]}</h3>
                        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                            <div>
                                <p style="margin:0; font-size:10px; color:gray;">DAYS DONE</p>
                                <p style="margin:0; font-weight:bold; font-size:20px;">{stat["Days Completed"]}</p>
                            </div>
                            <div style="text-align:right;">
                                <p style="margin:0; font-size:10px; color:gray;">CONSISTENCY</p>
                                <p style="margin:0; font-weight:bold; font-size:22px; color:{ethos_green};">{stat["Consistency"]:.1f}%</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Log and Synchronize habits to view the Performance Matrix.")

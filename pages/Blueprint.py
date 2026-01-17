import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query

st.set_page_config(layout="wide", page_title="Blueprint", page_icon="🗺️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user_email
st.title("🗺️ Strategic Blueprint")

# DATA ENGINE
raw_data = fetch_query("SELECT task_description, category, timeframe, priority, progress FROM future_tasks WHERE user_email=%s", (user,))
df = pd.DataFrame(raw_data, columns=["Description", "Category", "Timeframe", "Priority", "Progress"])
df['Status Bar'] = df['Progress']

# STRATEGY MAP
st.subheader("Strategic Resource Mapping")
if not df.empty:
    fig = px.sunburst(df, path=['Category', 'Priority', 'Description'], values='Progress', color='Category', color_discrete_sequence=px.colors.qualitative.Bold)
    # FIX: Restore bold separation lines
    fig.update_traces(marker_line_width=3, marker_line_color="#121212", insidetextorientation='radial')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# MASTER TABLE
st.subheader("System Master Table")
time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("🎯 Filter", options=time_options)
display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

# FIX: Separate columns. Status Bar removes duplicate % via format=""
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="bp_editor",
    column_config={
        "Status Bar": st.column_config.ProgressColumn("Status", min_value=0, max_value=100, format=""),
        "Progress": st.column_config.NumberColumn("Manual %", min_value=0, max_value=100, format="%d"),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=time_options[1:])
    }
)

if st.button("Synchronize System Blueprint", use_container_width=True):
    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    for _, row in edited_df.iterrows():
        if row["Description"]:
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], int(row["Progress"]))
            )
    st.rerun()

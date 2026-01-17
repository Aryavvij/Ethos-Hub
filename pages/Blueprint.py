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

# --- 4. THE STRATEGY BRIDGE (RESTORED PERCENTAGES) ---
st.subheader("Strategic Resource Mapping")
if not df.empty:
    # Adding a display label for the Sunburst that includes the %
    chart_df = df.copy()
    chart_df['Display_Label'] = chart_df['Description'].str.upper() + "<br>" + chart_df['Progress'].astype(str) + "%"
    
    fig = px.sunburst(
        chart_df, 
        path=['Category', 'Priority', 'Display_Label'], 
        values='Progress', 
        color='Category', 
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Restore Bold separation lines and percentage visibility
    fig.update_traces(
        marker_line_width=3, 
        marker_line_color="#121212", 
        insidetextorientation='radial',
        textinfo="label" # This ensures our Display_Label (Name + %) shows up
    )
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- 5. SYSTEM MASTER TABLE (CONSOLIDATED STATUS) ---
st.subheader("System Master Table")
time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("🎯 Filter View by Timeframe", options=time_options)

display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

# COLUMN CONFIGURATION: Consolidating the last 3 columns into one interactive 'Status'
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="blueprint_editor_v2",
    column_config={
        "Progress": st.column_config.ProgressColumn(
            "Status & Progress",
            help="Slide the bar to update percentage",
            min_value=0,
            max_value=100,
            format="%d%%", # This shows the % alongside the bar
            step=1,
        ),
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
    st.success("Blueprint Synced.")
    st.rerun()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Blueprint", page_icon="🗺️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🗺️ Strategic Blueprint")

# --- 2. DATA ENGINE ---
raw_data = fetch_query("SELECT task_description, category, timeframe, priority, progress FROM future_tasks WHERE user_email=%s", (user,))
df = pd.DataFrame(raw_data, columns=["Description", "Category", "Timeframe", "Priority", "Progress"])

# --- 3. TOP LEVEL OVERVIEW (Metrics) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Initiatives", len(df))
with m2:
    high_prio = len(df[df["Priority"].str.contains("High", na=False)]) if not df.empty else 0
    st.metric("High Priority", high_prio)
with m3:
    avg_prog = int(df["Progress"].mean()) if not df.empty else 0
    st.metric("Avg. Completion", f"{avg_prog}%")
with m4:
    ready = len(df[df["Progress"] >= 80]) if not df.empty else 0
    st.metric("Ready to Deploy", ready)

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# --- 4. THE STRATEGY BRIDGE (Sunburst Map) ---
st.subheader("Strategic Resource Mapping")
chart_data = df[df['Progress'] > 0].copy()

if not chart_data.empty:
    fig = px.sunburst(
        chart_data, 
        path=['Category', 'Priority', 'Description'], 
        values='Progress',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Initiate progress to generate the Strategy Map.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SYSTEM MASTER TABLE (Dual Progress Update) ---
st.subheader("System Master Table")

time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("🎯 Filter View by Timeframe", options=time_options)

# Create a 'Visual' column for the bar display
df['Visual Progress'] = df['Progress']

display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

# COLUMN CONFIGURATION: Visual Bar + Editable Number
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="master_blueprint_editor",
    column_config={
        "Visual Progress": st.column_config.ProgressColumn(
            "Status",
            help="Visual progress line",
            format="%d%%",
            min_value=0,
            max_value=100,
        ),
        "Progress": st.column_config.NumberColumn(
            "Edit %",
            help="Double-click to set progress (0-100)",
            format="%d%%",
            min_value=0,
            max_value=100,
            step=1,
        ),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=time_options[1:])
    }
)

if st.button("Synchronize System Blueprint", use_container_width=True):
    # Process updates
    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    
    # We loop through the edited_df to save changes
    for _, row in edited_df.iterrows():
        if row["Description"]:
            # Cleanly handle row updates
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], int(row["Progress"]))
            )
    st.success("Blueprint Synced.")
    st.rerun()

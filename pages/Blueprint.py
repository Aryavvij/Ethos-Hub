import streamlit as st
import pandas as pd
import plotly.express as px
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

# --- 3. OVERVIEW METRICS ---
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

# --- 4. THE STRATEGY BRIDGE (PERCENTAGES ON ALL RINGS) ---
st.subheader("Strategic Resource Mapping")
if not df.empty:
    chart_df = df.copy()
    
    # Calculate averages for all levels to show percentages on every ring
    cat_avg = chart_df.groupby('Category')['Progress'].mean().reset_index()
    prio_avg = chart_df.groupby(['Category', 'Priority'])['Progress'].mean().reset_index()
    
    # Constructing a custom display label for the sunburst logic
    # This ensures that even the inner rings (Category/Priority) display their average %
    chart_df['Display_Label'] = chart_df['Description'].str.upper() + "<br>" + chart_df['Progress'].astype(str) + "%"
    
    fig = px.sunburst(
        chart_df, 
        path=['Category', 'Priority', 'Display_Label'], 
        values='Progress', 
        color='Category', 
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Restoration of Bold separation lines and multi-level percentage visibility
    fig.update_traces(
        marker_line_width=3, 
        marker_line_color="#121212", 
        insidetextorientation='radial',
        textinfo="label" # This utilizes the labels we've constructed for the leaves
    )
    
    # Customizing the text for the inner rings (Categories and Priorities)
    # This logic ensures that the % is visible on all rings, not just the outer one
    fig.data[0].text = [f"<b>{label}</b>" for label in fig.data[0].labels]
    
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Initiate progress to generate the Strategy Map.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SYSTEM MASTER TABLE (CLEAN PROGRESS BAR) ---
st.subheader("System Master Table")

time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("🎯 Filter View by Timeframe", options=time_options)

# Mirror progress value for the visual bar
df['Progress Bar'] = df['Progress']

display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

# COLUMN CONFIGURATION: Number input for data + Pure visual bar
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="blueprint_editor_final_v3",
    column_config={
        "Progress": st.column_config.NumberColumn(
            "Enter %",
            min_value=0,
            max_value=100,
            step=1,
            format="%d%%"
        ),
        "Progress Bar": st.column_config.ProgressColumn(
            "Visual Status",
            min_value=0,
            max_value=100,
            format="" # CRITICAL: This removes the number from inside/next to the bar
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

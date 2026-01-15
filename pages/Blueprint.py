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

# --- 3. PIPELINE METRICS (TOP) ---
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

st.markdown("---")

# --- 4. VISUAL STRATEGY (The Fixed Sunburst) ---
col_chart, col_filter = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Strategic Resource Mapping")
    if not df.empty:
        # FIX: Create a copy for the chart so we don't change the actual data
        chart_df = df.copy()
        
        # FIX: Assign a minimum value of 1 to Progress for the chart 
        # so that 0% tasks (like your first row) are still visible.
        chart_df['Display_Size'] = chart_df['Progress'].apply(lambda x: max(x, 5))

        # Professional Sunburst Construction
        fig = px.sunburst(
            chart_df, 
            path=['Category', 'Priority', 'Description'], # Added Description for a 3rd layer
            values='Display_Size',
            color='Category',
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data={'Progress': True, 'Display_Size': False} # Hide the hacky size from user
        )
        
        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10), 
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found. Add tasks to the table below.")

with col_filter:
    st.subheader("🎯 Viewport Control")
    horizon = st.radio(
        "Filter your view:",
        ["Full System", "This Week", "Couple Weeks", "Couple Months", "This Vacation/This Semester", "1 Year", "Someday", "Maybe"],
        horizontal=False
    )
    
    # Filter logic
    if horizon == "Full System":
        filtered_df = df
    else:
        filtered_df = df[df["Timeframe"] == horizon]

# --- 5. MASTER TABLE ---
st.subheader(f"Initiatives: {horizon}")

edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{horizon}",
    column_config={
        "Progress": st.column_config.NumberColumn("Progress %", min_value=0, max_value=100, format="%d%%"),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=["This Week", "Couple Weeks", "Couple Months", "This Vacation/This Semester", "1 Year", "Someday", "Maybe"])
    }
)

if st.button("Synchronize System Blueprint", use_container_width=True, key="sync_btn"):
    # Delete old data for this user
    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    
    # Re-insert from the editor
    for _, row in edited_df.iterrows():
        if row["Description"]:
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], row["Progress"])
            )
    st.success("Blueprint Synced.")
    st.rerun()

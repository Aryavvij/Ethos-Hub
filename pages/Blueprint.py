import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Blueprint", page_icon="🗺️")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🗺️ Strategic Blueprint")

# --- 3. DATA ENGINE ---
raw_data = fetch_query("SELECT task_description, category, timeframe, priority, progress FROM future_tasks WHERE user_email=%s", (user,))
df = pd.DataFrame(raw_data, columns=["Description", "Category", "Timeframe", "Priority", "Progress"])

# Ensure we have data for metrics
if df.empty:
    df = pd.DataFrame(columns=["Description", "Category", "Timeframe", "Priority", "Progress"])

# --- 4. PIPELINE METRICS (TOP) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Initiatives", len(df))
with m2:
    high_prio = len(df[df["Priority"].str.contains("High", na=False)])
    st.metric("High Priority", high_prio)
with m3:
    avg_prog = int(df["Progress"].mean()) if not df.empty else 0
    st.metric("Avg. Completion", f"{avg_prog}%")
with m4:
    # Logic: Tasks > 80% are "Ready to Deploy" to Weekly Planner
    ready = len(df[df["Progress"] >= 80])
    st.metric("Ready to Deploy", ready, help="Tasks near completion")

st.markdown("---")

# --- 5. VISUAL STRATEGY & FILTERS ---
col_chart, col_filter = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Strategic Resource Mapping")
    if not df.empty:
        # Sunburst: Category (Inner) -> Priority (Outer)
        # Using progress to define the slice sizes
        fig = px.sunburst(
            df, 
            path=['Category', 'Priority'], 
            values='Progress',
            color='Category',
            color_discrete_sequence=px.colors.qualitative.G10,
            template="plotly_dark"
        )
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet to generate Sunburst Map.")

with col_filter:
    st.subheader("Viewport Control")
    st.write("Filter your view to specific horizons:")
    
    # Horizontal filter buttons using a radio selector styled as a menu
    horizon = st.radio(
        "Select Horizon",
        ["Full System", "Next Month", "6 Months", "1 Year", "Someday/Maybe"],
        horizontal=False,
        label_visibility="collapsed"
    )
    
    # Filtering Logic
    if horizon == "Full System":
        filtered_df = df
    else:
        filtered_df = df[df["Timeframe"] == horizon]

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. MASTER INITIATIVE TABLE ---
st.subheader(f"Initiatives: {horizon}")

edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{horizon}", # Key changes with filter to reset view properly
    column_config={
        "Progress": st.column_config.NumberColumn("Progress %", min_value=0, max_value=100, format="%d%%"),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=["Next Month", "6 Months", "1 Year", "Someday", "Maybe"])
    }
)

# SYNC BUTTON (Must be Full System Sync)
if st.button("Synchronize System Blueprint", use_container_width=True):
    # If the user is in a filtered view, we need to be careful not to delete the hidden rows.
    # So we fetch all data, update only the filtered rows, then save.
    
    # For a professional, clean sync, we'll save the currently edited rows 
    # and merge them with the existing database data.
    
    if horizon == "Full System":
        # Delete and replace all
        execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
        for _, row in edited_df.iterrows():
            if row["Description"]:
                execute_query(
                    "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], row["Progress"])
                )
    else:
        # In a filtered view, we only update the rows currently visible
        for _, row in edited_df.iterrows():
            if row["Description"]:
                execute_query(
                    """UPDATE future_tasks SET category=%s, timeframe=%s, priority=%s, progress=%s 
                       WHERE user_email=%s AND task_description=%s""",
                    (row["Category"], row["Timeframe"], row["Priority"], row["Progress"], user, row["Description"])
                )
    
    st.success(f"Blueprint updated for {horizon}")
    st.rerun()

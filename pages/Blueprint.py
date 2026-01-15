import streamlit as st
import pandas as pd
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Blueprint")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🗺️ The Blueprint")

with st.container(border=True):
    st.subheader("🛰️ Future Initiatives")
    raw_future = fetch_query("SELECT id, task_description, category, timeframe, priority FROM future_tasks WHERE user_email=%s", (user,))
    
    # Ensure columns match even if data is empty
    future_df = pd.DataFrame(raw_future, columns=["ID", "Description", "Category", "Timeframe", "Priority"])

    if future_df.empty:
        # Create an empty row with None for ID
        future_df = pd.DataFrame([{"ID": None, "Description": "", "Category": "Career", "Timeframe": "Someday", "Priority": "🧊 Low"}])

    # Safely drop ID column only if it exists
    cols_to_show = [c for c in future_df.columns if c != "ID"]
    display_df = future_df[cols_to_show]

    edited_future = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        key="blueprint_editor_v1" # Unique key for the editor
    )

    # ADDED UNIQUE KEY HERE to fix the DuplicateElementId error
    if st.button("💾 Sync Blueprint", use_container_width=True, key="sync_blueprint_btn_unique"):
        execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
        for _, row in edited_future.iterrows():
            if row["Description"]:
                execute_query(
                    "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority) VALUES (%s, %s, %s, %s, %s)",
                    (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"])
                )
        st.success("Blueprint Synced.")
        st.rerun()

    if st.button("💾 Sync Blueprint", use_container_width=True):
        execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
        for _, row in edited_future.iterrows():
            if row["Description"]:
                execute_query(
                    "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority) VALUES (%s, %s, %s, %s, %s)",
                    (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"])
                )
        st.success("Blueprint Synced.")
        st.rerun()

    if st.button("💾 Sync Blueprint", use_container_width=True):
        # Transactional Save
        execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
        for _, row in edited_future.iterrows():
            if row["Description"]:
                execute_query(
                    "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority) VALUES (%s, %s, %s, %s, %s)",
                    (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"])
                )
        st.success("Blueprint Synced.")
        st.rerun()

# --- 4. STRATEGIC ANALYSIS ---
st.markdown("---")
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Resource Allocation (By Category)")
    if not edited_future.empty:
        import plotly.express as px
        # Visualizing where your future energy is going
        fig = px.pie(
            edited_future, 
            names='Category', 
            hole=0.5, 
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Critical Objectives (🔥 High Priority)")
    # Filter only High Priority items to keep focus sharp
    high_prio = edited_future[edited_future["Priority"] == "🔥 High"]
    if not high_prio.empty:
        for task in high_prio["Description"]:
            st.markdown(f"""
                <div style="background: rgba(255, 75, 75, 0.1); border-left: 5px solid #ff4b4b; padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                    <strong>{task}</strong>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No high-priority initiatives currently logged.")

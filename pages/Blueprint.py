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

# --- 4. VISUAL STRATEGY ---
col_chart, col_side = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Strategic Resource Mapping")
    chart_df = df[df['Progress'] > 0].copy()
    
    if not chart_df.empty:
        # Create the Sunburst
        fig = px.sunburst(
            chart_df, 
            path=['Category', 'Priority', 'Description'], 
            values='Progress',
            color='Category',
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        
        # APPLY BOLD SEPARATION AND CORRECT HOVER INFO
        fig.update_traces(
            marker_line_width=3,
            marker_line_color="#121212",
            # We use percent parent (lowercase with space) as per Plotly requirements
            hoverinfo="label+value+percent parent",
            # Display logic: Only show text if it's the outermost ring (leaf)
            textinfo="label+percent parent",
            insidetextorientation='radial'
        )
        
        fig.update_layout(
            margin=dict(t=10, l=10, r=10, b=10), 
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active progress to map. Tasks at 0% are hidden from this view.")

with col_side:
    st.subheader("🎯 Viewport Control")
    horizon = st.radio(
        "Filter your view:",
        ["Full System", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"],
        horizontal=False
    )
    
    st.markdown("---")
    
    st.subheader("📊 Active Task Completion")
    active_tasks = df[df['Progress'] > 0].sort_values(by="Progress", ascending=False)
    
    if not active_tasks.empty:
        for idx, row in active_tasks.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Description']}**")
                
                fig_ring = go.Figure(go.Pie(
                    values=[row['Progress'], 100-row['Progress']],
                    hole=.7,
                    marker_colors=['#76b372', '#1a1a1a'],
                    showlegend=False,
                    textinfo='none'
                ))
                fig_ring.update_layout(
                    height=140, margin=dict(t=5, b=5, l=5, r=5),
                    paper_bgcolor='rgba(0,0,0,0)',
                    annotations=[dict(text=f"{row['Progress']}%", x=0.5, y=0.5, font_size=18, showarrow=False, font_color="#76b372")]
                )
                st.plotly_chart(fig_ring, use_container_width=True, config={'displayModeBar': False})
                st.caption(f"{row['Category']} | {row['Priority']}")
    else:
        st.caption("No active progress tracked.")

# --- 5. FILTER LOGIC & MASTER TABLE ---
if horizon == "Full System":
    filtered_df = df
else:
    filtered_df = df[df["Timeframe"] == horizon]

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
        "Timeframe": st.column_config.SelectboxColumn(options=["This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"])
    }
)

if st.button("Synchronize System Blueprint", use_container_width=True, key="sync_btn"):
    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    for _, row in edited_df.iterrows():
        if row["Description"]:
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], row["Progress"])
            )
    st.success("Blueprint Synced.")
    st.rerun()

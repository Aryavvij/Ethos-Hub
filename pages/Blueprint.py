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

# Reduced spacing
st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# --- 4. VISUAL STRATEGY (Corrected Average Logic) ---
col_chart, col_filter = st.columns([2.5, 1], gap="small")

with col_chart:
    st.subheader("Strategic Resource Mapping")
    chart_df = df[df['Progress'] > 0].copy()
    
    if not chart_df.empty:
        # MANUAL HIERARCHY BUILDING FOR ACCURATE AVERAGES
        ids = ["Total System"]
        labels = ["Total System"]
        parents = [""]
        values = [chart_df['Progress'].mean()]

        # 1. Categories
        for cat in chart_df['Category'].unique():
            cat_avg = chart_df[chart_df['Category'] == cat]['Progress'].mean()
            ids.append(cat)
            labels.append(cat)
            parents.append("Total System")
            values.append(cat_avg)

            # 2. Priorities within Categories
            for prio in chart_df[chart_df['Category'] == cat]['Priority'].unique():
                p_id = f"{cat}-{prio}"
                p_avg = chart_df[(chart_df['Category'] == cat) & (chart_df['Priority'] == prio)]['Progress'].mean()
                ids.append(p_id)
                labels.append(prio)
                parents.append(cat)
                values.append(p_avg)

                # 3. Individual Tasks
                tasks = chart_df[(chart_df['Category'] == cat) & (chart_df['Priority'] == prio)]
                for _, row in tasks.iterrows():
                    ids.append(row['Description'])
                    labels.append(row['Description'])
                    parents.append(p_id)
                    values.append(row['Progress'])

        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(line=dict(color='#121212', width=3), colors=px.colors.qualitative.Bold),
            hovertemplate='<b>%{label}</b><br>Avg Progress: %{value:.1f}%<extra></extra>',
            texttemplate='<b>%{label}</b><br>%{value:.1f}%',
            insidetextorientation='radial'
        ))

        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active progress to map. Add progress to your initiatives below.")

with col_filter:
    st.subheader("🎯 Viewport")
    horizon = st.radio(
        "Filter Horizon:",
        ["Full System", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"],
        horizontal=False
    )

# --- 5. INITIATIVES TABLE (TIGHT SPACING) ---
st.markdown("<div style='margin-top:-30px;'></div>", unsafe_allow_html=True)
st.subheader(f"Initiatives: {horizon}")

if horizon == "Full System":
    filtered_df = df
else:
    filtered_df = df[df["Timeframe"] == horizon]

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
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], int(row["Progress"]))
            )
    st.success("Blueprint Synced.")
    st.rerun()

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

# --- 4. THE STRATEGY BRIDGE (Centered Sunburst with Global Averages) ---
st.subheader("Strategic Resource Mapping")
chart_data = df[df['Progress'] > 0].copy()

if not chart_data.empty:
    # GLOBAL AVERAGES CALCULATION
    # This ensures "Medium" shows the same avg across all categories
    cat_averages = chart_data.groupby('Category')['Progress'].mean().to_dict()
    prio_global_avg = chart_data.groupby('Priority')['Progress'].mean().to_dict()

    fig = px.sunburst(
        chart_data, 
        path=['Category', 'Priority', 'Description'], 
        values='Progress',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    new_labels = []
    for i, label in enumerate(fig.data[0].labels):
        parent = fig.data[0].parents[i]
        
        # 1. Category Level (Outer root)
        if label in cat_averages and parent == "":
            new_labels.append(f"<b>{label}</b><br>{cat_averages[label]:.1f}%")
        
        # 2. Priority Level (Global Average Logic)
        elif label in ["High", "Medium", "Low"]:
            avg = prio_global_avg.get(label, 0)
            new_labels.append(f"<b>{label}</b><br>{avg:.1f}%")
            
        # 3. Task Level (Actual Progress)
        else:
            val = fig.data[0].values[i]
            new_labels.append(f"<b>{label}</b><br>{val}%")

    fig.update_traces(
        textinfo="text", text=new_labels,
        marker_line_width=3, marker_line_color="#121212",
        hovertemplate='<b>%{label}</b><extra></extra>',
        insidetextorientation='radial'
    )

    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Initiate progress to generate the Strategy Map.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SYSTEM MASTER TABLE (With Integrated Filter & Editing) ---
st.subheader("System Master Table")

# Integrated Timeframe Filter
time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("🎯 Filter View by Timeframe", options=time_options)

if filter_choice == "All":
    display_df = df
else:
    display_df = df[df["Timeframe"] == filter_choice]

edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="master_blueprint_editor",
    column_config={
        "Progress": st.column_config.NumberColumn(
            "Progress %",
            help="Double-click to edit completion percentage",
            format="%d%%",
            min_value=0,
            max_value=100,
        ),
        "Category": st.column_config.SelectboxColumn(
            options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]
        ),
        "Priority": st.column_config.SelectboxColumn(
            options=["High", "Medium", "Low"]
        ),
        "Timeframe": st.column_config.SelectboxColumn(
            options=["This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
        )
    }
)

if st.button("Synchronize System Blueprint", use_container_width=True):
    # If filtering is on, we update the main DF with edited changes before saving
    if filter_choice != "All":
        df.update(edited_df)
    else:
        df = edited_df

    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    for _, row in df.iterrows():
        if row["Description"]:
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], int(row["Progress"]))
            )
    st.success("Blueprint Synced.")
    st.rerun()

import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from utils import render_sidebar

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Blueprint", page_icon="🗺️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()
    
render_sidebar()

user = st.session_state.user_email
st.title("Academic Trajectory")


# --- 2. DATA ENGINE ---
raw_data = fetch_query("SELECT task_description, category, timeframe, priority, progress FROM future_tasks WHERE user_email=%s", (user,))
df = pd.DataFrame(raw_data, columns=["Description", "Category", "Timeframe", "Priority", "Progress"])

# --- 3. OVERVIEW METRICS (UPDATED TO 1 DECIMAL PLACE) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Initiatives", len(df))
with m2:
    high_prio = len(df[df["Priority"].str.contains("High", na=False)]) if not df.empty else 0
    st.metric("High Priority", high_prio)
with m3:
    avg_prog = df["Progress"].mean() if not df.empty else 0
    # FIX: Metric now shows one decimal point
    st.metric("Avg. Completion", f"{avg_prog:.1f}%")
with m4:
    ready = len(df[df["Progress"] >= 80]) if not df.empty else 0
    st.metric("Almost Finished", ready)

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# --- 4. THE STRATEGY BRIDGE (FIXED: 1 DECIMAL POINT AVERAGING) ---
st.subheader("Strategic Progress Mapping")
if not df.empty:
    chart_df = df.copy()
    
    # 1. Calculate Global Averages
    cat_avg = chart_df.groupby('Category')['Progress'].mean().to_dict()
    global_prio_avg = chart_df.groupby('Priority')['Progress'].mean().to_dict()
    
    fig = px.sunburst(
        chart_df, 
        path=['Category', 'Priority', 'Description'], 
        values='Progress', 
        color='Category', 
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # 2. Logic to update labels with 1 decimal point formatting
    new_labels = []
    for i, label in enumerate(fig.data[0].labels):
        parent = fig.data[0].parents[i]
        
        # CATEGORY LEVEL (Inner Ring)
        if label in cat_avg and parent == "":
            val = cat_avg[label]
            new_labels.append(f"<b>{label.upper()}</b><br>{val:.1f}%")
        
        # PRIORITY LEVEL (Middle Ring - GLOBAL AVERAGE)
        elif label in ["High", "Medium", "Low"]:
            val = global_prio_avg.get(label, 0)
            new_labels.append(f"<b>{label}</b><br>{val:.1f}%")
            
        # DESCRIPTION LEVEL (Outer Ring)
        else:
            # For specific leaves, show the decimal if it exists
            val = float(fig.data[0].values[i])
            new_labels.append(f"<b>{label.upper()}</b><br>{val:.1f}%")

    fig.update_traces(
        textinfo="text",
        text=new_labels,
        marker_line_width=3, 
        marker_line_color="#121212", 
        insidetextorientation='radial'
    )
    
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Initiate progress to generate the Strategy Map.")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SYSTEM MASTER TABLE ---
st.subheader("Task Input Table")
time_options = ["All", "This Week", "Couple Weeks", "Couple Months", "This Vacation", "This Semester", "1 Year", "Someday", "Maybe"]
filter_choice = st.selectbox("Filter View by Timeframe", options=time_options)

display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="blueprint_decimal_v1",
    column_config={
        "Progress": st.column_config.NumberColumn(
            "Progress %",
            min_value=0,
            max_value=100,
            step=0.1, # Allows you to enter decimals manually too
            format="%.1f%%"
        ),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=time_options[1:])
    }
)

if st.button("Synchronize Tasks Blueprint", use_container_width=True):
    execute_query("DELETE FROM future_tasks WHERE user_email=%s", (user,))
    for _, row in edited_df.iterrows():
        if row["Description"]:
            execute_query(
                "INSERT INTO future_tasks (user_email, task_description, category, timeframe, priority, progress) VALUES (%s, %s, %s, %s, %s, %s)",
                (user, row["Description"], row["Category"], row["Timeframe"], row["Priority"], float(row["Progress"]))
            )
    st.success("Blueprint Synced.")
    st.rerun()

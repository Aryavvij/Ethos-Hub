import streamlit as st
import pandas as pd
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="The Pantheon")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("🏆 The Pantheon")
st.caption("Personal Rankings & Definitve All-Time Favorites")

# --- 3. CATEGORY MANAGEMENT ---
# Fetch all existing categories for this user to populate the dropdown
existing_cats = fetch_query("SELECT DISTINCT category FROM rankings WHERE user_email=%s", (user,))
default_cats = ["Movies", "Restaurants", "Books", "Travel", "Music"]
cat_list = sorted(list(set(default_cats + [row[0] for row in existing_cats])))

col_a, col_b = st.columns([3, 1])
with col_a:
    category = st.selectbox("Select Ranking Category", cat_list)
with col_b:
    new_cat = st.text_input("Add New Category", placeholder="e.g. Anime")
    if st.button("➕ Add", use_container_width=True):
        if new_cat:
            category = new_cat # Switch to the new category
            st.rerun()

st.markdown("---")

# --- 4. RANKING ENGINE ---
st.subheader(f"The {category} Hierarchy")
st.info("The order determines the rank. Row 1 is #1. Use the 'Add Row' button at the bottom of the table to expand.")

# Fetch data for current category
raw_data = fetch_query(
    "SELECT item_name FROM rankings WHERE user_email=%s AND category=%s ORDER BY rank_order ASC", 
    (user, category)
)
rank_df = pd.DataFrame(raw_data, columns=["Item Name"])

if rank_df.empty:
    rank_df = pd.DataFrame([{"Item Name": ""}])

# Add a visual Rank number for the user (UI only)
rank_df.insert(0, "Rank", range(1, len(rank_df) + 1))

edited_rank = st.data_editor(
    rank_df, 
    num_rows="dynamic", 
    use_container_width=True, 
    hide_index=True,
    key=f"editor_{category}",
    column_config={
        "Rank": st.column_config.NumberColumn(disabled=True, help="Automatically assigned based on position"),
        "Item Name": st.column_config.TextColumn(placeholder="Enter title/name...")
    }
)

# --- 5. SYNC LOGIC ---
if st.button(f"💾 Sync {category} Rankings", use_container_width=True, key="sync_pantheon"):
    # Delete old rankings for this category only
    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, category))
    
    # Insert new ordered list
    for i, row in edited_rank.iterrows():
        if row["Item Name"] and str(row["Item Name"]).strip() != "":
            execute_query(
                "INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                (user, category, row["Item Name"], i)
            )
    st.success(f"Hierarchy for {category} has been updated.")
    st.rerun()

# --- 6. VISUAL TOP 3 ---
if len(edited_rank) >= 1 and edited_rank.iloc[0]["Item Name"]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🥇 The Podium")
    p1, p2, p3 = st.columns(3)
    
    # Display top 3 items in stylish cards
    for idx, col in enumerate([p1, p2, p3]):
        if idx < len(edited_rank) and edited_rank.iloc[idx]["Item Name"]:
            with col:
                st.markdown(f"""
                    <div style="background: rgba(118, 179, 114, 0.1); border: 1px solid #76b372; padding: 20px; border-radius: 10px; text-align: center;">
                        <span style="font-size: 24px;">{'🥇' if idx==0 else '🥈' if idx==1 else '🥉'}</span>
                        <h3 style="margin: 10px 0; color: #76b372;">{edited_rank.iloc[idx]['Item Name']}</h3>
                    </div>
                """, unsafe_allow_html=True)

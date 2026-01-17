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
st.caption("Personal Rankings & Global Hierarchies")

# --- 3. INPUT SECTION (TOP) ---
with st.container(border=True):
    st.subheader("Add to the Pantheon")
    # c1, c2 for inputs, c3 for the button
    c1, c2, c3 = st.columns([2, 2, 1])
    
    with c1:
        cat_name = st.text_input("Category", placeholder="e.g., Best Books")
    with c2:
        item_name = st.text_input("Item Name", placeholder="e.g., Meditations")
    with c3:
        # Pushes button down to align with the text boxes exactly
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Add Item", use_container_width=True):
            if cat_name and item_name:
                # Find current max order for this category to append to end
                res = fetch_query("SELECT COUNT(*) FROM rankings WHERE user_email=%s AND category=%s", (user, cat_name))
                new_order = res[0][0] if res else 0
                execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                              (user, cat_name, item_name, new_order))
                st.rerun()

st.markdown("---")

# --- 4. SEARCH INTERFACE (FIX 6) ---
st.subheader("🏛️ Search the Pantheon")
search_query = st.text_input("Filter tables by title...", placeholder="Type category name here...", key="p_search", label_visibility="collapsed")

# --- 5. UNIFORM RANKING GRID ---
categories_raw = fetch_query("SELECT DISTINCT category FROM rankings WHERE user_email=%s", (user,))
all_categories = [row[0] for row in categories_raw]

# Apply Search Filter
if search_query:
    categories = [c for c in all_categories if search_query.lower() in c.lower()]
else:
    categories = all_categories

if not categories:
    st.info("No matching rankings found.")
else:
    # Display tables in a 3-column grid
    cols = st.columns(3)
    
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            # Professional Header for each table
            st.markdown(f"""
                <div style="background:#76b372; padding:5px 15px; border-radius:5px 5px 0 0; color:white; font-weight:bold; margin-bottom:-5px;">
                    {cat.upper()}
                </div>
            """, unsafe_allow_html=True)
            
            # Fetch data for this specific category
            raw_data = fetch_query(
                "SELECT id, item_name FROM rankings WHERE user_email=%s AND category=%s ORDER BY rank_order ASC", 
                (user, cat)
            )
            df = pd.DataFrame(raw_data, columns=["ID", "Item"])
            
            # Editable Data Editor
            edited_df = st.data_editor(
                df.drop(columns=["ID"]),
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_{cat}",
                column_config={
                    "Item": st.column_config.TextColumn("Entry", help="Click to edit name")
                }
            )
            
            # Action Buttons for this specific table
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"Save {cat[:10]}", key=f"save_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    for i, row in edited_df.iterrows():
                        if row["Item"]:
                            execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                                         (user, cat, row["Item"], i))
                    st.success("Saved")
            with b2:
                if st.button(f"Delete {cat[:10]}", key=f"del_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

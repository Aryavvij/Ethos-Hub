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
# --- PANTHEON ADDER ---
with st.container(border=True):
    st.subheader("Add to the Pantheon")
    # Using specific ratios: 2 parts for inputs, 1 part for the action
    c1, c2, c3 = st.columns([2, 2, 1])
    
    with c1:
        cat_name = st.text_input("Category", placeholder="e.g., Best Books")
    with c2:
        item_name = st.text_input("Item Name", placeholder="e.g., Meditations")
    with c3:
        # This invisible spacer pushes the button down to align with the text boxes
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Add Item", use_container_width=True):
            # Save logic here
            st.rerun()

st.markdown("---")

# --- 4. UNIFORM RANKING GRID ---
# Fetch all unique categories created by the user
categories_raw = fetch_query("SELECT DISTINCT category FROM rankings WHERE user_email=%s", (user,))
categories = [row[0] for row in categories_raw]

if not categories:
    st.info("No rankings created yet. Use the input section above to start your first list.")
else:
    # Display tables in a 3-column grid for uniformity
    cols = st.columns(3)
    
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            st.markdown(f"#### {cat}")
            
            # Fetch data for this specific category
            raw_data = fetch_query(
                "SELECT id, item_name FROM rankings WHERE user_email=%s AND category=%s ORDER BY rank_order ASC", 
                (user, cat)
            )
            df = pd.DataFrame(raw_data, columns=["ID", "Item"])
            
            # Editable Data Editor (Order = Rank)
            # Placeholder error fixed by removing the keyword
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
                if st.button(f"Save {cat}", key=f"save_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    for i, row in edited_df.iterrows():
                        if row["Item"]:
                            execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                                         (user, cat, row["Item"], i))
                    st.success("Saved")
            with b2:
                if st.button(f"Delete {cat}", key=f"del_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

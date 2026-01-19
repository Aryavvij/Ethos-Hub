import streamlit as st
import pandas as pd
from database import execute_query, fetch_query

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="The Pantheon", page_icon="🏛️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
st.title("🏆 The Pantheon")
st.caption("Universal Knowledge Repository: Structured Rankings & Deep Notes")

# --- 2. DUAL-MODE INPUT SECTION ---
with st.container(border=True):
    st.subheader("Expand the Pantheon")
    t1, t2 = st.tabs(["📊 Create Ranking Table", "📝 Create Master Note"])
    
    with t1:
        c1, c2, c3 = st.columns([2, 2, 1])
        cat_name = c1.text_input("Category Title", placeholder="e.g., Top Tech Stocks", key="new_cat")
        item_name = c2.text_input("Initial Entry", placeholder="e.g., NVIDIA", key="new_item")
        if c3.button("➕ Initialize Table", use_container_width=True):
            if cat_name and item_name:
                execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                              (user, cat_name, item_name, 0))
                st.rerun()
    
    with t2:
        n1, n2, n3 = st.columns([2, 2, 1])
        note_title = n1.text_input("Note Title", placeholder="e.g., Thesis Observations", key="new_note_title")
        if n3.button("📝 Initialize Note", use_container_width=True):
            if note_title:
                # We save notes as a special category with a '[NOTE]' prefix
                execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                              (user, f"[NOTE] {note_title}", "", 0))
                st.rerun()

st.markdown("---")

# --- 3. SEARCH & FILTER ---
search_query = st.text_input("🔍 Search Pantheon Assets...", placeholder="Search categories or notes...", key="p_search")

# --- 4. THE UNIFORM GRID ---
raw_cats = fetch_query("SELECT DISTINCT category FROM rankings WHERE user_email=%s", (user,))
all_categories = [row[0] for row in raw_cats]

if search_query:
    categories = [c for c in all_categories if search_query.lower() in c.lower()]
else:
    categories = all_categories

if not categories:
    st.info("The Pantheon is currently empty.")
else:
    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        with cols[idx % 3]:
            # --- RENDER NOTE MODE ---
            if cat.startswith("[NOTE]"):
                display_title = cat.replace("[NOTE] ", "").upper()
                st.markdown(f"""
                    <div style="background:#4a90e2; padding:5px 15px; border-radius:5px 5px 0 0; color:white; font-weight:bold; margin-bottom:-5px;">
                        📝 {display_title}
                    </div>
                """, unsafe_allow_html=True)
                
                # Fetch note content (stored in item_name)
                note_data = fetch_query("SELECT item_name FROM rankings WHERE user_email=%s AND category=%s LIMIT 1", (user, cat))
                current_text = note_data[0][0] if note_data else ""
                
                edited_note = st.text_area("Content", value=current_text, height=250, key=f"note_area_{cat}", label_visibility="collapsed")
                
                nb1, nb2 = st.columns(2)
                if nb1.button(f"Save Note", key=f"save_n_{cat}", use_container_width=True):
                    execute_query("UPDATE rankings SET item_name=%s WHERE user_email=%s AND category=%s", (edited_note, user, cat))
                    st.success("Archived")
                if nb2.button(f"Delete Note", key=f"del_n_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    st.rerun()

            # --- RENDER TABLE MODE ---
            else:
                st.markdown(f"""
                    <div style="background:#76b372; padding:5px 15px; border-radius:5px 5px 0 0; color:white; font-weight:bold; margin-bottom:-5px;">
                        📊 {cat.upper()}
                    </div>
                """, unsafe_allow_html=True)
                
                raw_table = fetch_query("SELECT item_name FROM rankings WHERE user_email=%s AND category=%s ORDER BY rank_order ASC", (user, cat))
                df = pd.DataFrame(raw_table, columns=["Entry"])
                
                edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"table_ed_{cat}")
                
                tb1, tb2 = st.columns(2)
                if tb1.button(f"Save Table", key=f"save_t_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    for i, row in edited_df.iterrows():
                        if row["Entry"]:
                            execute_query("INSERT INTO rankings (user_email, category, item_name, rank_order) VALUES (%s, %s, %s, %s)",
                                         (user, cat, row["Entry"], i))
                    st.success("Synced")
                if tb2.button(f"Delete Table", key=f"del_t_{cat}", use_container_width=True):
                    execute_query("DELETE FROM rankings WHERE user_email=%s AND category=%s", (user, cat))
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

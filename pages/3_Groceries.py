import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Groceries", page_icon="🥗", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

render_page_header("Groceries", "🥗", "groceries")
st.write("**Simple grocery list manager**")

# Add Grocery Form
st.subheader("➕ Add Grocery Item")

with st.form("add_grocery_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        grocery_name = st.text_input("Grocery Item *", placeholder="e.g., Milk, Bread, Eggs")
    
    with col2:
        submitted = st.form_submit_button("Add Grocery", use_container_width=True)
    
    if submitted:
        if grocery_name.strip():
            create_item(
                title=grocery_name,
                item_type="GROCERY",
                status="TODO"
            )
            st.success(f"✅ '{grocery_name}' added to grocery list!")
            st.rerun()
        else:
            st.error("Grocery item name is required!")

st.divider()

# Display Groceries
st.subheader("🛒 Grocery List")

groceries = get_items_by_type("GROCERY", exclude_archived=True)

if not groceries:
    st.info("Your grocery list is empty. Add items above!")
else:
    # Separate pending and completed
    pending = [g for g in groceries if g['status'] == 'TODO']
    completed = [g for g in groceries if g['status'] == 'COMPLETED']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Pending", len(pending))
    with col2:
        st.metric("✅ Completed", len(completed))
    
    st.divider()
    
    # Pending Groceries
    if pending:
        st.subheader("📝 Pending Items")
        
        for grocery in pending:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{grocery['title']}**")
                created = datetime.fromisoformat(grocery['created_at']).strftime("%b %d, %Y")
                st.caption(f"Added: {created}")
            
            with col2:
                if st.button("✅ Complete", key=f"complete_{grocery['id']}"):
                    update_item_status(grocery['id'], 'COMPLETED')
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{grocery['id']}", type="secondary"):
                    delete_item(grocery['id'])
                    st.rerun()
            
            st.divider()
    
    # Completed Groceries
    if completed:
        with st.expander(f"✅ Recently Completed ({len(completed)})"):
            for grocery in completed[:10]:  # Show only last 10 completed
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"~~{grocery['title']}~~")
                    if grocery['completed_at']:
                        completed_date = datetime.fromisoformat(grocery['completed_at']).strftime("%b %d, %Y")
                        st.caption(f"Completed: {completed_date}")
                
                with col2:
                    if st.button("🔄 Undo", key=f"undo_{grocery['id']}"):
                        update_item_status(grocery['id'], 'TODO')
                        st.rerun()

# Quick Add Section
st.divider()
st.subheader("⚡ Quick Add Common Items")

common_items = [
    "🥛 Milk", "🍞 Bread", "🥚 Eggs", "🍚 Rice", "🧈 Butter",
    "🧀 Cheese", "🍅 Tomatoes", "🥔 Potatoes", "🧅 Onions", "🥕 Carrots"
]

cols = st.columns(5)
for idx, item in enumerate(common_items):
    with cols[idx % 5]:
        if st.button(item, key=f"quick_{idx}", use_container_width=True):
            item_name = item.split(" ", 1)[1]  # Remove emoji
            create_item(
                title=item_name,
                item_type="GROCERY",
                status="TODO"
            )
            st.success(f"Added {item_name}!")
            st.rerun()

import streamlit as st
from database import get_archived_items, delete_item, update_item_status
from datetime import datetime
from theme import render_page_header, add_pwa_support
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Archive", page_icon="📦", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

render_page_header("Archive", "📦", "archive")
st.write("**View completed and archived items**")

# Filter options
col1, col2 = st.columns(2)

with col1:
    filter_type = st.selectbox("Filter by Type", ["All", "TASK", "PURCHASE", "GROCERY"])

with col2:
    filter_status = st.selectbox("Filter by Status", ["All", "COMPLETED", "ARCHIVED"])

# Get archived items
if filter_type == "All":
    items = get_archived_items()
else:
    items = get_archived_items(item_type=filter_type)

# Apply status filter
if filter_status != "All":
    items = [item for item in items if item['status'] == filter_status]

st.divider()

# Display count
st.write(f"**Showing {len(items)} items**")

if not items:
    st.info("No archived items yet. Complete some tasks, purchases, or groceries to see them here!")
else:
    # Display items
    for item in items:
        # Item type emoji
        item_type_emoji = {
            'TASK': '📋',
            'PURCHASE': '🛒',
            'GROCERY': '🥗'
        }.get(item['item_type'], '📌')
        
        # Status emoji
        status_emoji = '✅' if item['status'] == 'COMPLETED' else '📦'
        
        with st.expander(f"{item_type_emoji} {status_emoji} {item['title']} ({item['item_type']})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type:** {item['item_type']}")
                st.write(f"**Status:** {item['status']}")
                
                if item['assigned_to']:
                    st.write(f"**Assigned To:** {item['assigned_to']}")
                
                if item['priority']:
                    priority_color = {
                        'High': '🔴',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }.get(item['priority'], '')
                    st.write(f"**Priority:** {item['priority']} {priority_color}")
            
            with col2:
                created = datetime.fromisoformat(item['created_at']).strftime("%b %d, %Y")
                st.write(f"**Created:** {created}")
                
                if item['completed_at']:
                    completed = datetime.fromisoformat(item['completed_at']).strftime("%b %d, %Y")
                    st.write(f"**Completed:** {completed}")
                
                if item['budget']:
                    st.write(f"**Budget:** ₹{item['budget']:.2f}")
            
            if item['purchase_link']:
                st.markdown(f"**🔗 Link:** [{item['purchase_link']}]({item['purchase_link']})")
            
            if item['notes']:
                st.write(f"**Notes:** {item['notes']}")
            
            st.divider()
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if item['status'] == 'COMPLETED' and st.button("📦 Archive", key=f"archive_{item['id']}"):
                    update_item_status(item['id'], 'ARCHIVED')
                    st.rerun()
            
            with col2:
                if item['status'] == 'ARCHIVED' and st.button("🔄 Restore", key=f"restore_{item['id']}"):
                    # Restore to TODO status
                    update_item_status(item['id'], 'TODO')
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete Permanently", key=f"delete_{item['id']}", type="secondary"):
                    delete_item(item['id'])
                    st.rerun()

# Summary Statistics
st.divider()
st.subheader("📊 Archive Summary")

col1, col2, col3, col4 = st.columns(4)

completed_count = len([i for i in items if i['status'] == 'COMPLETED'])
archived_count = len([i for i in items if i['status'] == 'ARCHIVED'])
task_count = len([i for i in items if i['item_type'] == 'TASK'])
purchase_count = len([i for i in items if i['item_type'] == 'PURCHASE'])

with col1:
    st.metric("✅ Completed", completed_count)

with col2:
    st.metric("📦 Archived", archived_count)

with col3:
    st.metric("📋 Tasks", task_count)

with col4:
    st.metric("🛒 Purchases", purchase_count)

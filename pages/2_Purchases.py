import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Purchases", page_icon="🛒", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

render_page_header("Purchases", "🛒", "purchases")
st.write("**Track Amazon, Flipkart, and online shopping**")

# Add Purchase Form
st.subheader("➕ Add New Purchase")

with st.form("add_purchase_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("Item Name *", placeholder="e.g., New Coffee Maker")
        budget = st.number_input("Budget (₹)", min_value=0.0, step=100.0)
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    
    with col2:
        purchase_link = st.text_input("Amazon/Flipkart URL", placeholder="https://...")
        notes = st.text_area("Notes", placeholder="Details, specifications, alternatives...")
    
    submitted = st.form_submit_button("Add Purchase", use_container_width=True)
    
    if submitted:
        if item_name.strip():
            create_item(
                title=item_name,
                item_type="PURCHASE",
                status="WISHLIST",
                priority=priority,
                budget=budget if budget > 0 else None,
                purchase_link=purchase_link if purchase_link else None,
                notes=notes if notes else None
            )
            st.success(f"✅ Purchase '{item_name}' added to wishlist!")
            st.rerun()
        else:
            st.error("Item name is required!")

st.divider()

# Display Purchases
st.subheader("🛍️ All Purchases")

purchases = get_items_by_type("PURCHASE", exclude_archived=True)

if not purchases:
    st.info("No purchases yet. Add your first purchase item above!")
else:
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox("Filter by Status", 
            ["All", "WISHLIST", "RESEARCHING", "READY_TO_BUY", "ORDERED", "DELIVERED", "INSTALLED"])
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"])
    
    # Apply filters
    filtered_purchases = purchases
    if filter_status != "All":
        filtered_purchases = [p for p in filtered_purchases if p['status'] == filter_status]
    if filter_priority != "All":
        filtered_purchases = [p for p in filtered_purchases if p['priority'] == filter_priority]
    
    st.write(f"**Showing {len(filtered_purchases)} of {len(purchases)} purchases**")
    
    # Status explanation
    with st.expander("ℹ️ Purchase Status Guide"):
        st.write("""
        - **WISHLIST**: Items you're considering
        - **RESEARCHING**: Comparing options and prices
        - **READY_TO_BUY**: Decided and ready to purchase
        - **ORDERED**: Order placed, waiting for delivery
        - **DELIVERED**: Received the item
        - **INSTALLED**: Set up and ready to use
        """)
    
    # Display purchases
    for purchase in filtered_purchases:
        status_emoji = {
            'WISHLIST': '💭',
            'RESEARCHING': '🔍',
            'READY_TO_BUY': '✅',
            'ORDERED': '📦',
            'DELIVERED': '🚚',
            'INSTALLED': '✨'
        }.get(purchase['status'], '🛒')
        
        priority_color = {
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(purchase.get('priority'), '')
        
        with st.expander(f"{status_emoji} {purchase['title']} {priority_color}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Status:** {purchase['status']}")
                if purchase['priority']:
                    st.write(f"**Priority:** {purchase['priority']}")
                if purchase['budget']:
                    st.write(f"**Budget:** ₹{purchase['budget']:.2f}")
            
            with col2:
                # Handle both datetime object (PostgreSQL) and string (SQLite)
                created_at = purchase['created_at']
                created = created_at.strftime("%b %d, %Y") if not isinstance(created_at, str) else datetime.fromisoformat(created_at).strftime("%b %d, %Y")
                st.write(f"**Added:** {created}")
                if purchase['completed_at']:
                    comp_at = purchase['completed_at']
                    completed = comp_at.strftime("%b %d, %Y") if not isinstance(comp_at, str) else datetime.fromisoformat(comp_at).strftime("%b %d, %Y")
                    st.write(f"**Completed:** {completed}")
            
            if purchase['purchase_link']:
                st.markdown(f"**🔗 Link:** [{purchase['purchase_link']}]({purchase['purchase_link']})")
            
            if purchase['notes']:
                st.write(f"**Notes:** {purchase['notes']}")
            
            st.divider()
            
            # Status change buttons
            st.write("**Change Status:**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                if st.button("💭", key=f"wishlist_{purchase['id']}", help="Wishlist"):
                    update_item_status(purchase['id'], 'WISHLIST')
                    st.rerun()
            
            with col2:
                if st.button("🔍", key=f"research_{purchase['id']}", help="Researching"):
                    update_item_status(purchase['id'], 'RESEARCHING')
                    st.rerun()
            
            with col3:
                if st.button("✅", key=f"ready_{purchase['id']}", help="Ready to Buy"):
                    update_item_status(purchase['id'], 'READY_TO_BUY')
                    st.rerun()
            
            with col4:
                if st.button("📦", key=f"ordered_{purchase['id']}", help="Ordered"):
                    update_item_status(purchase['id'], 'ORDERED')
                    st.rerun()
            
            with col5:
                if st.button("🚚", key=f"delivered_{purchase['id']}", help="Delivered"):
                    update_item_status(purchase['id'], 'DELIVERED')
                    st.rerun()
            
            with col6:
                if st.button("✨", key=f"installed_{purchase['id']}", help="Installed"):
                    update_item_status(purchase['id'], 'INSTALLED')
                    st.rerun()
            
            # Delete button
            if st.button("🗑️ Delete", key=f"delete_{purchase['id']}", type="secondary"):
                delete_item(purchase['id'])
                st.rerun()

# Summary
st.divider()
st.subheader("📊 Summary")
col1, col2, col3 = st.columns(3)

wishlist_count = len([p for p in purchases if p['status'] == 'WISHLIST'])
researching_count = len([p for p in purchases if p['status'] == 'RESEARCHING'])
ordered_count = len([p for p in purchases if p['status'] == 'ORDERED'])

with col1:
    st.metric("💭 Wishlist", wishlist_count)
with col2:
    st.metric("🔍 Researching", researching_count)
with col3:
    st.metric("📦 Ordered", ordered_count)

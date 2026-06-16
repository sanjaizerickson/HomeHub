import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support, render_bottom_navigation, get_page_style
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Shopping", page_icon="🛒", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

# Apply theme with sidebar styling
st.markdown(get_page_style('shopping'), unsafe_allow_html=True)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Shopping Card Styling - Compact for Mobile */
    .purchase-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #48bb78;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Horizontal Progress Bar */
    .progress-bar-horizontal {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0;
        margin: 0.5rem 0;
    }
    
    .progress-dot {
        font-size: 1.5rem;
        opacity: 0.3;
        transition: all 0.3s;
    }
    
    .progress-dot.active {
        opacity: 1;
        transform: scale(1.2);
    }
    
    .progress-dot.completed {
        opacity: 0.7;
    }
    
    .progress-line {
        flex: 1;
        height: 2px;
        background: rgba(255, 255, 255, 0.1);
        margin: 0 0.5rem;
        position: relative;
    }
    
    .progress-line.active {
        background: #48bb78;
    }
    
    /* Priority Badges - Compact */
    .priority-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 0.25rem;
    }
    .priority-high { background: #fee2e2; color: #991b1b; }
    .priority-medium { background: #fef3c7; color: #92400e; }
    .priority-low { background: #d1fae5; color: #065f46; }
    
    /* Metadata - Compact */
    .purchase-meta {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .purchase-card {
            padding: 0.5rem;
        }
        .stButton > button {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.85rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

render_page_header("Shopping", "🛒", "shopping")

# Collapsible Add Shopping Item Form
with st.expander("➕ Add Shopping Item", expanded=False):
    with st.form("add_shopping_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Item Name *", placeholder="e.g., New Coffee Maker")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        with col2:
            purchase_link = st.text_input("Amazon/Flipkart URL", placeholder="https://...")
            notes = st.text_area("Notes", placeholder="Details, specifications, alternatives...")
        
        submitted = st.form_submit_button("✅ Add to Shopping List", use_container_width=True, type="primary")
        
        if submitted:
            if item_name.strip():
                create_item(
                    title=item_name,
                    item_type="PURCHASE",
                    status="RESEARCH",
                    priority=priority,
                    purchase_link=purchase_link if purchase_link else None,
                    notes=notes if notes else None
                )
                st.success(f"✅ '{item_name}' added to shopping list!")
                st.rerun()
            else:
                st.error("Item name is required!")

st.divider()

# Get shopping items
purchases = get_items_by_type("PURCHASE", exclude_archived=True)

if not purchases:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: rgba(72, 187, 120, 0.1); border-radius: 12px;'>
        <h2 style='color: #48bb78;'>🛒 No Shopping Items Yet!</h2>
        <p style='color: #6b7280; font-size: 1.1rem;'>Start by adding your first item above</p>
        <p style='font-size: 2.5rem; margin-top: 1rem;'>🛍️</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Filter Pills
    st.markdown("**🔍 Filters:**")
    col1, col2, col3 = st.columns([3, 2, 7])
    
    with col1:
        status_filter = st.selectbox("Status", 
            ["All", "RESEARCH", "WISHLIST", "ORDERED", "DELIVERED"], 
            label_visibility="collapsed")
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "Low", "Medium", "High"], label_visibility="collapsed")
    
    # Apply filters
    filtered_purchases = purchases
    if status_filter != "All":
        filtered_purchases = [p for p in filtered_purchases if p['status'] == status_filter]
    if priority_filter != "All":
        filtered_purchases = [p for p in filtered_purchases if p['priority'] == priority_filter]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(filtered_purchases))
    with col2:
        research_count = len([p for p in filtered_purchases if p['status'] == 'RESEARCH'])
        st.metric("🔍 Research", research_count)
    with col3:
        wishlist_count = len([p for p in filtered_purchases if p['status'] == 'WISHLIST'])
        st.metric("💭 Wishlist", wishlist_count)
    with col4:
        ordered_count = len([p for p in filtered_purchases if p['status'] == 'ORDERED'])
        st.metric("📦 Ordered", ordered_count)
    
    st.divider()
    
    # Status stages mapping (4 stages only)
    status_stages = ['RESEARCH', 'WISHLIST', 'ORDERED', 'DELIVERED']
    stage_emojis = {'RESEARCH': '🔍', 'WISHLIST': '💭', 'ORDERED': '📦', 'DELIVERED': '✅'}
    stage_labels = {'RESEARCH': 'Research', 'WISHLIST': 'Wishlist', 'ORDERED': 'Ordered', 'DELIVERED': 'Delivered'}
    
    # Separate active and delivered items
    active_purchases = [p for p in filtered_purchases if p['status'] != 'DELIVERED']
    delivered_purchases = [p for p in filtered_purchases if p['status'] == 'DELIVERED']
    
    # Display active purchases as cards
    if active_purchases:
        st.markdown("### 🛒 Active Shopping Items")
        for purchase in active_purchases:
            # Priority badge
            priority_class = f"priority-{purchase['priority'].lower()}"
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(purchase['priority'], "")
            
            # Current stage - map old statuses to new ones
            current_stage = purchase['status']
            # Handle old statuses
            status_mapping = {
                'WISHLIST': 'WISHLIST',
                'RESEARCHING': 'RESEARCH',
                'READY_TO_BUY': 'WISHLIST',  # Map old status to Wishlist
                'INSTALLED': 'DELIVERED'  # Map old status to Delivered
            }
            current_stage = status_mapping.get(current_stage, current_stage)
            
            # Get current index safely
            try:
                current_index = status_stages.index(current_stage)
            except ValueError:
                # If status not in list, default to first stage
                current_index = 0
                current_stage = status_stages[0]
            
            # Build horizontal progress bar
            progress_html = '<div class="progress-bar-horizontal">'
            for i, stage in enumerate(status_stages):
                # Determine dot class
                dot_class = 'progress-dot'
                if i < current_index:
                    dot_class += ' completed'
                elif i == current_index:
                    dot_class += ' active'
                
                progress_html += f'<span class="{dot_class}">{stage_emojis[stage]}</span>'
                
                # Add connecting line (except after last dot)
                if i < len(status_stages) - 1:
                    line_class = 'progress-line'
                    if i < current_index:
                        line_class += ' active'
                    progress_html += f'<div class="{line_class}"></div>'
            
            progress_html += '</div>'
            
            # Card container
            with st.container():
                # Build card HTML with progress bar inline
                card_html = f"""
                <div class="purchase-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                        <h4 style="margin: 0; color: #48bb78; font-size: 1.15rem; font-weight: 600;">{purchase['title']}</h4>
                        <span class="priority-badge {priority_class}">{priority_emoji}</span>
                    </div>
                    {progress_html}
                    <div class="purchase-meta">
                        📅 {purchase['created_at'].strftime("%b %d") if not isinstance(purchase['created_at'], str) else datetime.fromisoformat(purchase['created_at']).strftime("%b %d")}
                        {' • 🔗 <a href="' + purchase['purchase_link'] + '" target="_blank" style="color: #48bb78;">Link</a>' if purchase['purchase_link'] else ''}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Actions row - compact
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    # Smart Next Stage button
                    if current_index < len(status_stages) - 1:
                        next_stage = status_stages[current_index + 1]
                        next_emoji = stage_emojis[next_stage]
                        next_label = stage_labels[next_stage]
                        if st.button(f"{next_emoji} {next_label}", key=f"next_{purchase['id']}", use_container_width=True, type="primary"):
                            update_item_status(purchase['id'], next_stage)
                            st.rerun()
                    else:
                        if st.button("🔄 Reopen", key=f"reopen_{purchase['id']}", use_container_width=True, type="primary"):
                            update_item_status(purchase['id'], 'RESEARCH')
                            st.rerun()
                
                with col2:
                    # Change status dropdown (collapsed)
                    with st.expander("⚙️ Change Status", expanded=False):
                        new_status = st.selectbox("Jump to Stage", 
                            status_stages,
                            index=current_index,
                            key=f"status_{purchase['id']}",
                            format_func=lambda x: f"{stage_emojis[x]} {stage_labels[x]}",
                            label_visibility="collapsed")
                        if st.button("Update", key=f"update_status_{purchase['id']}", use_container_width=True):
                            update_item_status(purchase['id'], new_status)
                            st.rerun()
                
                with col3:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{purchase['id']}", use_container_width=True):
                        delete_item(purchase['id'])
                        st.rerun()
                
                # Notes if available
                if purchase['notes']:
                    with st.expander("📝 Notes", expanded=False):
                        st.caption(purchase['notes'])
                
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Display delivered items in expander
    if delivered_purchases:
        st.markdown("---")
        with st.expander(f"✅ Delivered Items ({len(delivered_purchases)})", expanded=False):
            for purchase in delivered_purchases:
                # Priority badge
                priority_class = f"priority-{purchase['priority'].lower()}"
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(purchase['priority'], "")
                
                # Card container
                with st.container():
                    st.markdown(f"""
                    <div class="purchase-card" style="opacity: 0.7;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <div>
                                <h3 style="margin: 0; color: #10b981; text-decoration: line-through;">{purchase['title']}</h3>
                            </div>
                            <div>
                                <span class="priority-badge {priority_class}">{priority_emoji} {purchase['priority']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Purchase link
                        if purchase['purchase_link']:
                            domain = "Amazon" if "amazon" in purchase['purchase_link'].lower() else ("Flipkart" if "flipkart" in purchase['purchase_link'].lower() else "Link")
                            st.markdown(f'<a href="{purchase["purchase_link"]}" target="_blank" class="link-preview">🔗 View on {domain}</a>', unsafe_allow_html=True)
                        
                        # Date info
                        created_at = purchase['created_at']
                        if isinstance(created_at, str):
                            created = datetime.fromisoformat(created_at).strftime("%b %d, %I:%M %p")
                        else:
                            created = created_at.strftime("%b %d, %I:%M %p")
                        st.caption(f"📅 Added: {created}")
                        
                        # Notes
                        if purchase['notes']:
                            with st.expander("📝 View Notes"):
                                st.write(purchase['notes'])
                    
                    with col2:
                        if st.button("🔄 Reopen", key=f"reopen_{purchase['id']}", use_container_width=True):
                            update_item_status(purchase['id'], 'RESEARCH')
                            st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_delivered_{purchase['id']}", type="secondary"):
                        delete_item(purchase['id'])
                        st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)

# Render bottom navigation
render_bottom_navigation('shopping')

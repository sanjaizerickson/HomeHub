import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support, render_bottom_navigation, get_page_style
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Groceries", page_icon="🥗", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

# Apply theme with sidebar styling
st.markdown(get_page_style('groceries'), unsafe_allow_html=True)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Grocery Item Styling */
    .grocery-item {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #10b981;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s;
    }
    
    .grocery-item:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(4px);
    }
    
    .grocery-item.completed {
        border-left-color: #6b7280;
        opacity: 0.7;
    }
    
    .grocery-checkbox {
        width: 24px;
        height: 24px;
        border-radius: 6px;
        border: 2px solid #10b981;
        background: transparent;
        cursor: pointer;
        margin-right: 1rem;
    }
    
    .grocery-checkbox.checked {
        background: #10b981;
    }
    
    .grocery-title {
        flex: 1;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .grocery-title.completed {
        text-decoration: line-through;
        color: #6b7280;
    }
    
    /* Category Headers */
    .category-header {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0) 100%);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    /* Quick Add Button */
    .quick-add-btn {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .quick-add-btn:hover {
        background: rgba(16, 185, 129, 0.2);
        border-color: rgba(16, 185, 129, 0.5);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

render_page_header("Groceries", "🥗", "groceries")

# Add Grocery Form
st.markdown("### ➕ Add Grocery Item")
with st.form("add_grocery_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        grocery_name = st.text_input("Grocery Item *", placeholder="e.g., Milk, Bread, Eggs", label_visibility="collapsed")
    
    with col2:
        submitted = st.form_submit_button("✅ Add", use_container_width=True, type="primary")
    
    if submitted:
        if grocery_name.strip():
            create_item(
                title=grocery_name,
                item_type="GROCERY",
                status="TODO"
            )
            st.success(f"✅ '{grocery_name}' added to list!")
            st.rerun()
        else:
            st.error("Item name is required!")

st.divider()

# Get groceries
groceries = get_items_by_type("GROCERY", exclude_archived=True)

if not groceries:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: rgba(16, 185, 129, 0.1); border-radius: 12px;'>
        <h2 style='color: #10b981;'>🥗 No Groceries Yet!</h2>
        <p style='color: #6b7280; font-size: 1.1rem;'>Use quick add buttons above or add manually</p>
        <p style='font-size: 2.5rem; margin-top: 1rem;'>🛒</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Separate pending and completed
    pending = [g for g in groceries if g['status'] == 'TODO']
    completed = [g for g in groceries if g['status'] == 'COMPLETED']
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Pending", len(pending))
    with col2:
        st.metric("✅ Completed", len(completed))
    
    st.divider()
    
    # Pending Groceries (Checkbox Style)
    if pending:
        st.markdown("### 📝 Shopping List")
        
        for grocery in pending:
            col1, col2, col3 = st.columns([0.5, 4, 1])
            
            with col1:
                # Checkbox style complete button
                if st.button("☐", key=f"check_{grocery['id']}", help="Mark as complete"):
                    update_item_status(grocery['id'], 'COMPLETED')
                    st.rerun()
            
            with col2:
                st.markdown(f"""
                <div style="padding-top: 0.5rem;">
                    <strong style="font-size: 1rem;">{grocery['title']}</strong>
                    <br>
                    <span style="font-size: 0.75rem; color: #6b7280;">Added: {
                        grocery['created_at'].strftime("%b %d, %I:%M %p") if not isinstance(grocery['created_at'], str) 
                        else datetime.fromisoformat(grocery['created_at']).strftime("%b %d, %I:%M %p")
                    }</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("🗑️", key=f"delete_{grocery['id']}", help="Delete item"):
                    delete_item(grocery['id'])
                    st.rerun()
            
            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Completed Groceries
    if completed:
        st.markdown("---")
        with st.expander(f"✅ Recently Completed ({len(completed)})", expanded=False):
            for grocery in completed[:20]:  # Show last 20 completed
                col1, col2, col3 = st.columns([0.5, 4, 1])
                
                with col1:
                    # Checked checkbox style undo button
                    if st.button("☑", key=f"uncheck_{grocery['id']}", help="Undo completion"):
                        update_item_status(grocery['id'], 'TODO')
                        st.rerun()
                
                with col2:
                    completed_at = grocery['completed_at']
                    completed_date = completed_at.strftime("%b %d, %I:%M %p") if not isinstance(completed_at, str) else datetime.fromisoformat(completed_at).strftime("%b %d, %I:%M %p")
                    st.markdown(f"""
                    <div style="padding-top: 0.5rem; opacity: 0.7;">
                        <span style="font-size: 1rem; text-decoration: line-through; color: #6b7280;">{grocery['title']}</span>
                        <br>
                        <span style="font-size: 0.75rem; color: #6b7280;">Completed: {completed_date}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("🗑️", key=f"delete_completed_{grocery['id']}", help="Delete item"):
                        delete_item(grocery['id'])
                        st.rerun()
                
                st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# Render bottom navigation
render_bottom_navigation('groceries')

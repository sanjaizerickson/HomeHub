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
    /* Grocery Card Styling */
    .grocery-card:hover {
        background: rgba(16, 185, 129, 0.12) !important;
        transform: translateX(2px);
    }
    
    .grocery-card-completed:hover {
        background: rgba(107, 114, 128, 0.12) !important;
        transform: translateX(2px);
    }
    
    /* Icon-only buttons - compact */
    div[data-testid="column"] button {
        min-width: 40px;
        padding: 0.5rem;
        font-size: 1.2rem;
    }
    
    /* Mobile optimization */
    @media (max-width: 768px) {
        div[data-testid="column"] button {
            min-width: 36px;
            padding: 0.4rem;
            font-size: 1.1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

render_page_header("Groceries", "🥗", "groceries")

# Add Grocery Form - Collapsed by default
with st.expander("➕ Add Grocery Item", expanded=False):
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(groceries))
    with col2:
        st.metric("📝 Pending", len(pending))
    with col3:
        st.metric("✅ Completed", len(completed))
    
    st.divider()
    
    # Pending Groceries (Super Compact - Buttons Inside Card)
    if pending:
        for grocery in pending:
            # Single row with card and inline buttons
            col_card, col_btn1, col_btn2 = st.columns([8, 1, 1])
            
            with col_card:
                # Compact card with item only
                card_html = f"""
                <div class="grocery-card" style="
                    background: rgba(16, 185, 129, 0.08);
                    border-left: 4px solid #10b981;
                    border-radius: 12px;
                    padding: 0.75rem 1rem;
                    display: flex;
                    align-items: center;
                    transition: all 0.2s;
                ">
                    <span style="font-size: 1.1rem; font-weight: 500; color: #10b981;">🥗</span>
                    <span style="font-size: 1.05rem; font-weight: 500; margin-left: 0.5rem;">{grocery['title']}</span>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
            
            with col_btn1:
                if st.button("✅", key=f"complete_{grocery['id']}", help="Complete"):
                    update_item_status(grocery['id'], 'COMPLETED')
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️", key=f"delete_{grocery['id']}", help="Delete"):
                    delete_item(grocery['id'])
                    st.rerun()
    
    # Completed Groceries
    if completed:
        st.markdown("---")
        with st.expander(f"✅ Recently Completed ({len(completed)})", expanded=False):
            for grocery in completed[:20]:  # Show last 20 completed
                # Single row with card and inline buttons
                col_card, col_btn1, col_btn2 = st.columns([8, 1, 1])
                
                with col_card:
                    # Compact card with strikethrough
                    card_html = f"""
                    <div class="grocery-card-completed" style="
                        background: rgba(107, 114, 128, 0.08);
                        border-left: 4px solid #6b7280;
                        border-radius: 12px;
                        padding: 0.75rem 1rem;
                        opacity: 0.7;
                        display: flex;
                        align-items: center;
                        transition: all 0.2s;
                    ">
                        <span style="font-size: 1.1rem;">✅</span>
                        <span style="font-size: 1.05rem; margin-left: 0.5rem; text-decoration: line-through; color: #6b7280;">{grocery['title']}</span>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                
                with col_btn1:
                    if st.button("🔄", key=f"undo_{grocery['id']}", help="Undo"):
                        update_item_status(grocery['id'], 'TODO')
                        st.rerun()
                
                with col_btn2:
                    if st.button("🗑️", key=f"delete_completed_{grocery['id']}", help="Delete"):
                        delete_item(grocery['id'])
                        st.rerun()

# Render bottom navigation
render_bottom_navigation('groceries')

import streamlit as st
from database import get_dashboard_metrics, get_recent_completed
from datetime import datetime
from theme import get_page_style, add_pwa_support
from auth import require_auth, render_logout_button

st.set_page_config(
    page_title="Home Hub - Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

# Apply theme
st.markdown(get_page_style('home'), unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>🏠 Home Hub</h1>
        <p style="margin: 0; opacity: 0.9;">Welcome Sanjai & Pradhiksha!</p>
    </div>
""", unsafe_allow_html=True)

# Get metrics
metrics = get_dashboard_metrics()

# Display metrics in columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📋 Pending Tasks", metrics['pending_tasks'])

with col2:
    st.metric("⚡ In Progress", metrics['tasks_in_progress'])

with col3:
    st.metric("🛒 Purchases", metrics['pending_purchases'])

with col4:
    st.metric("🥗 Groceries", metrics['pending_groceries'])

with col5:
    st.metric("✅ Completed", metrics['completed_this_month'])

st.divider()

# Recent Activity Section
st.subheader("📊 Recent Activity")

recent = get_recent_completed(10)

if recent:
    st.write(f"**Latest {len(recent)} Completed Items**")
    
    for item in recent:
        item_type_emoji = {
            'TASK': '📋',
            'PURCHASE': '🛒',
            'GROCERY': '🥗'
        }.get(item['item_type'], '📌')
        
        # Handle both datetime object (PostgreSQL) and string (SQLite)
        if item['completed_at']:
            comp_at = item['completed_at']
            completed_date = comp_at.strftime("%b %d, %Y") if not isinstance(comp_at, str) else datetime.fromisoformat(comp_at).strftime("%b %d, %Y")
        else:
            completed_date = "N/A"
        
        with st.expander(f"{item_type_emoji} {item['title']} - {completed_date}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {item['item_type']}")
                if item['assigned_to']:
                    st.write(f"**Assigned To:** {item['assigned_to']}")
            with col2:
                if item['priority']:
                    st.write(f"**Priority:** {item['priority']}")
                if item['budget']:
                    st.write(f"**Budget:** ₹{item['budget']}")
            
            if item['notes']:
                st.write(f"**Notes:** {item['notes']}")
else:
    st.info("No completed items yet. Start tracking your tasks, purchases, and groceries!")

st.divider()

# Quick Tips
col1, col2 = st.columns(2)

with col1:
    st.info("💡 **Tip:** Use the sidebar to navigate between Tasks, Purchases, and Groceries.")

with col2:
    st.success("🎯 Keep your home organized and stay on top of shared responsibilities!")

import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Tasks", page_icon="📋", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

render_page_header("Tasks", "📋", "tasks")

# Add Task Form
st.subheader("➕ Add New Task")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        task_title = st.text_input("Task Title *", placeholder="e.g., Fix kitchen sink")
        assigned_to = st.selectbox("Assigned To", ["Sanjai", "Pradhiksha", "Both"])
    
    with col2:
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        notes = st.text_area("Notes", placeholder="Additional details...")
    
    submitted = st.form_submit_button("Add Task", use_container_width=True)
    
    if submitted:
        if task_title.strip():
            create_item(
                title=task_title,
                item_type="TASK",
                status="TODO",
                assigned_to=assigned_to,
                priority=priority,
                notes=notes if notes else None
            )
            st.success(f"✅ Task '{task_title}' added successfully!")
            st.rerun()
        else:
            st.error("Task title is required!")

st.divider()

# Display Tasks
st.subheader("📋 All Tasks")

tasks = get_items_by_type("TASK", exclude_archived=True)

if not tasks:
    st.info("No tasks yet. Add your first task above!")
else:
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "TODO", "IN_PROGRESS", "COMPLETED"])
    with col2:
        filter_assigned = st.selectbox("Filter by Assigned To", ["All", "Sanjai", "Pradhiksha", "Both"])
    with col3:
        filter_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"])
    
    # Apply filters
    filtered_tasks = tasks
    if filter_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t['status'] == filter_status]
    if filter_assigned != "All":
        filtered_tasks = [t for t in filtered_tasks if t['assigned_to'] == filter_assigned]
    if filter_priority != "All":
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == filter_priority]
    
    st.write(f"**Showing {len(filtered_tasks)} of {len(tasks)} tasks**")
    
    # Display tasks
    for task in filtered_tasks:
        with st.expander(f"{'✅' if task['status'] == 'COMPLETED' else '⏳'} {task['title']} - {task['status']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Assigned To:** {task['assigned_to']}")
                st.write(f"**Priority:** {task['priority']}")
            
            with col2:
                st.write(f"**Status:** {task['status']}")
                created = datetime.fromisoformat(task['created_at']).strftime("%b %d, %Y %I:%M %p")
                st.write(f"**Created:** {created}")
            
            with col3:
                if task['completed_at']:
                    completed = datetime.fromisoformat(task['completed_at']).strftime("%b %d, %Y %I:%M %p")
                    st.write(f"**Completed:** {completed}")
            
            if task['notes']:
                st.write(f"**Notes:** {task['notes']}")
            
            st.divider()
            
            # Actions
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📝 TODO", key=f"todo_{task['id']}", disabled=task['status'] == 'TODO'):
                    update_item_status(task['id'], 'TODO')
                    st.rerun()
            
            with col2:
                if st.button("⚡ In Progress", key=f"progress_{task['id']}", disabled=task['status'] == 'IN_PROGRESS'):
                    update_item_status(task['id'], 'IN_PROGRESS')
                    st.rerun()
            
            with col3:
                if st.button("✅ Completed", key=f"complete_{task['id']}", disabled=task['status'] == 'COMPLETED'):
                    update_item_status(task['id'], 'COMPLETED')
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{task['id']}", type="secondary"):
                    delete_item(task['id'])
                    st.rerun()

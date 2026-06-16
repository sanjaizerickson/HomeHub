import streamlit as st
from database import create_item, get_items_by_type, update_item_status, delete_item
from datetime import datetime
from theme import render_page_header, add_pwa_support, render_bottom_navigation, get_page_style
from auth import require_auth, render_logout_button

st.set_page_config(page_title="Home Hub - Tasks", page_icon="📋", layout="wide")

# Add PWA support
add_pwa_support()

# Require authentication
require_auth()

# Render logout button in sidebar
render_logout_button()

# Apply theme with sidebar styling
st.markdown(get_page_style('tasks'), unsafe_allow_html=True)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Task Card Styling */
    .task-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Priority Badges */
    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .priority-high { background: #fee2e2; color: #991b1b; }
    .priority-medium { background: #fef3c7; color: #92400e; }
    .priority-low { background: #d1fae5; color: #065f46; }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-todo { background: #f3f4f6; color: #374151; }
    .status-progress { background: #dbeafe; color: #1e40af; }
    .status-done { background: #d1fae5; color: #065f46; }
    
    /* Assignee Badge */
    .assignee-badge {
        background: #e0e7ff;
        color: #3730a3;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Quick action buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

render_page_header("Tasks", "📋", "tasks")

# Collapsible Add Task Form
with st.expander("➕ Add New Task", expanded=False):
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_title = st.text_input("Task Title *", placeholder="e.g., Fix kitchen sink")
            assigned_to = st.selectbox("Assigned To", ["Sanjai", "Pradhiksha", "Both"])
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            notes = st.text_area("Notes", placeholder="Additional details...")
        
        submitted = st.form_submit_button("✅ Add Task", use_container_width=True, type="primary")
        
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

# Get tasks
tasks = get_items_by_type("TASK", exclude_archived=True)

if not tasks:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px;'>
        <h2 style='color: #667eea;'>📋 No Tasks Yet!</h2>
        <p style='color: #6b7280; font-size: 1.1rem;'>Start by adding your first task above</p>
        <p style='font-size: 2.5rem; margin-top: 1rem;'>🎉</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Filter Pills (horizontal chips)
    st.markdown("**🔍 Filters:**")
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "TODO", "IN_PROGRESS", "COMPLETED"], label_visibility="collapsed")
    with col2:
        assigned_filter = st.selectbox("Assigned", ["All", "Sanjai", "Pradhiksha", "Both"], label_visibility="collapsed")
    with col3:
        priority_filter = st.selectbox("Priority", ["All", "Low", "Medium", "High"], label_visibility="collapsed")
    
    # Apply filters
    filtered_tasks = tasks
    if status_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t['status'] == status_filter]
    if assigned_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t['assigned_to'] == assigned_filter]
    if priority_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority_filter]
    
    # Count by status
    todo_count = len([t for t in filtered_tasks if t['status'] == 'TODO'])
    progress_count = len([t for t in filtered_tasks if t['status'] == 'IN_PROGRESS'])
    done_count = len([t for t in filtered_tasks if t['status'] == 'COMPLETED'])
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(filtered_tasks))
    with col2:
        st.metric("📝 To Do", todo_count)
    with col3:
        st.metric("⚡ In Progress", progress_count)
    with col4:
        st.metric("✅ Done", done_count)
    
    st.divider()
    
    # Separate active and completed tasks
    active_tasks = [t for t in filtered_tasks if t['status'] != 'COMPLETED']
    completed_tasks = [t for t in filtered_tasks if t['status'] == 'COMPLETED']
    
    # Display active tasks as cards
    if active_tasks:
        st.markdown("### 📋 Active Tasks")
        for task in active_tasks:
            # Priority badge HTML
            priority_class = f"priority-{task['priority'].lower()}"
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task['priority'], "")
            
            # Status badge HTML
            status_class = {
                'TODO': 'status-todo',
                'IN_PROGRESS': 'status-progress',
                'COMPLETED': 'status-done'
            }.get(task['status'], 'status-todo')
            
            status_emoji = {
                'TODO': '📝',
                'IN_PROGRESS': '⚡',
                'COMPLETED': '✅'
            }.get(task['status'], '📝')
            
            # Card container
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <h3 style="margin: 0; color: #667eea;">{task['title']}</h3>
                        </div>
                        <div>
                            <span class="priority-badge {priority_class}">{priority_emoji} {task['priority']}</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 0.75rem;">
                        <span class="status-badge {status_class}">{status_emoji} {task['status'].replace('_', ' ')}</span>
                        <span class="assignee-badge">👤 {task['assigned_to']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Task details and actions in same row
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Date info
                    created_at = task['created_at']
                    if isinstance(created_at, str):
                        created = datetime.fromisoformat(created_at).strftime("%b %d, %I:%M %p")
                    else:
                        created = created_at.strftime("%b %d, %I:%M %p")
                    
                    st.caption(f"📅 Created: {created}")
                    
                    if task['notes']:
                        with st.expander("📝 View Notes"):
                            st.write(task['notes'])
                
                with col2:
                    # Quick status cycle button
                    next_status = {
                        'TODO': ('IN_PROGRESS', '⚡ Start'),
                        'IN_PROGRESS': ('COMPLETED', '✅ Done'),
                        'COMPLETED': ('TODO', '🔄 Reopen')
                    }.get(task['status'], ('TODO', '📝 To Do'))
                    
                    if st.button(next_status[1], key=f"quick_{task['id']}", use_container_width=True, type="primary"):
                        update_item_status(task['id'], next_status[0])
                        st.rerun()
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{task['id']}", type="secondary"):
                    delete_item(task['id'])
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Display completed tasks in expander
    if completed_tasks:
        st.markdown("---")
        with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
            for task in completed_tasks:
                # Priority badge HTML
                priority_class = f"priority-{task['priority'].lower()}"
                priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task['priority'], "")
                
                # Card container
                with st.container():
                    st.markdown(f"""
                    <div class="task-card" style="opacity: 0.7;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <div>
                                <h3 style="margin: 0; color: #10b981; text-decoration: line-through;">{task['title']}</h3>
                            </div>
                            <div>
                                <span class="priority-badge {priority_class}">{priority_emoji} {task['priority']}</span>
                            </div>
                        </div>
                        <div style="margin-bottom: 0.75rem;">
                            <span class="assignee-badge">👤 {task['assigned_to']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Completed date
                        if task['completed_at']:
                            completed_at = task['completed_at']
                            if isinstance(completed_at, str):
                                completed = datetime.fromisoformat(completed_at).strftime("%b %d, %I:%M %p")
                            else:
                                completed = completed_at.strftime("%b %d, %I:%M %p")
                            st.caption(f"✅ Completed: {completed}")
                        
                        if task['notes']:
                            with st.expander("📝 View Notes"):
                                st.write(task['notes'])
                    
                    with col2:
                        if st.button("🔄 Reopen", key=f"reopen_{task['id']}", use_container_width=True):
                            update_item_status(task['id'], 'TODO')
                            st.rerun()
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"delete_completed_{task['id']}", type="secondary"):
                        delete_item(task['id'])
                        st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)

# Render bottom navigation
render_bottom_navigation('tasks')

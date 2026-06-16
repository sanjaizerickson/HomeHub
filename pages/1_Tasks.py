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
    /* Task Card Styling - Compact for Mobile */
    .task-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #667eea;
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
        background: #667eea;
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
    .task-meta {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.25rem;
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .task-card {
            padding: 0.5rem;
        }
        .stButton > button {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.85rem !important;
        }
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
            
            # Status progress stages
            status_stages = ['TODO', 'IN_PROGRESS', 'COMPLETED']
            status_emojis = ['📝', '⚡', '✅']
            current_stage = task['status']
            current_index = status_stages.index(current_stage) if current_stage in status_stages else 0
            
            # Build horizontal progress bar
            progress_html = '<div class="progress-bar-horizontal">'
            for i, (stage, emoji) in enumerate(zip(status_stages, status_emojis)):
                # Determine dot class
                dot_class = 'progress-dot'
                if i < current_index:
                    dot_class += ' completed'
                elif i == current_index:
                    dot_class += ' active'
                
                progress_html += f'<span class="{dot_class}">{emoji}</span>'
                
                # Add connecting line (except after last dot)
                if i < len(status_stages) - 1:
                    line_class = 'progress-line'
                    if i < current_index:
                        line_class += ' active'
                    progress_html += f'<div class="{line_class}"></div>'
            
            progress_html += '</div>'
            
            # Card container
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                        <h4 style="margin: 0; color: #667eea; font-size: 1rem;">{task['title']}</h4>
                        <span class="priority-badge {priority_class}">{priority_emoji}</span>
                    </div>
                    {progress_html}
                    <div class="task-meta">
                        👤 {task['assigned_to']} • 📅 {task['created_at'].strftime("%b %d") if not isinstance(task['created_at'], str) else datetime.fromisoformat(task['created_at']).strftime("%b %d")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Actions row - compact
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    # Quick action button
                    next_status = {
                        'TODO': ('IN_PROGRESS', '⚡ Start'),
                        'IN_PROGRESS': ('COMPLETED', '✅ Done'),
                        'COMPLETED': ('TODO', '🔄 Reopen')
                    }.get(task['status'], ('TODO', '📝 To Do'))
                    
                    if st.button(next_status[1], key=f"quick_{task['id']}", use_container_width=True, type="primary"):
                        update_item_status(task['id'], next_status[0])
                        st.rerun()
                
                with col2:
                    # Change status dropdown (collapsed)
                    with st.expander("⚙️ Change Status", expanded=False):
                        new_status = st.selectbox("Select Status", 
                            ['TODO', 'IN_PROGRESS', 'COMPLETED'],
                            index=status_stages.index(current_stage),
                            key=f"status_{task['id']}",
                            label_visibility="collapsed")
                        if st.button("Update", key=f"update_status_{task['id']}", use_container_width=True):
                            update_item_status(task['id'], new_status)
                            st.rerun()
                
                with col3:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{task['id']}", use_container_width=True):
                        delete_item(task['id'])
                        st.rerun()
                
                # Notes if available
                if task['notes']:
                    with st.expander("📝 Notes", expanded=False):
                        st.caption(task['notes'])
                
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

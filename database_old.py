import sqlite3
from datetime import datetime, timedelta

# Database connection
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()


def migrate_db():
    """Migrate existing database to add missing columns"""
    # Get existing columns
    cursor.execute("PRAGMA table_info(items)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    # Add missing columns one by one
    columns_to_add = {
        'priority': 'TEXT',
        'budget': 'REAL',
        'purchase_link': 'TEXT',
        'notes': 'TEXT',
        'completed_at': 'TIMESTAMP'
    }
    
    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE items ADD COLUMN {column_name} {column_type}")
                conn.commit()
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError:
                pass  # Column might already exist


def init_db():
    """Initialize database with required schema"""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        item_type TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_to TEXT,
        priority TEXT,
        budget REAL,
        purchase_link TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    """)
    conn.commit()
    
    # Run migration for existing databases
    migrate_db()


def create_item(title, item_type, status, assigned_to=None, priority=None, 
                budget=None, purchase_link=None, notes=None):
    """Create a new item in the database"""
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO items (title, item_type, status, assigned_to, priority, 
                          budget, purchase_link, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, item_type, status, assigned_to, priority, budget, purchase_link, notes, created_at))
    conn.commit()
    return cursor.lastrowid


def get_all_items():
    """Get all items from database"""
    cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_items_by_type(item_type, exclude_archived=True):
    """Get items filtered by type"""
    if exclude_archived:
        cursor.execute("""
            SELECT * FROM items 
            WHERE item_type = ? AND status != 'ARCHIVED'
            ORDER BY created_at DESC
        """, (item_type,))
    else:
        cursor.execute("""
            SELECT * FROM items 
            WHERE item_type = ?
            ORDER BY created_at DESC
        """, (item_type,))
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_item_counts():
    """Get counts of different item types by status"""
    cursor.execute("""
        SELECT item_type, status, COUNT(*) as count
        FROM items
        WHERE status != 'ARCHIVED' AND status != 'COMPLETED'
        GROUP BY item_type, status
    """)
    return cursor.fetchall()


def update_item_status(item_id, status):
    """Update item status and set completed_at if status is COMPLETED"""
    completed_at = datetime.now().isoformat() if status == 'COMPLETED' else None
    if status == 'COMPLETED':
        cursor.execute("""
            UPDATE items 
            SET status = ?, completed_at = ?
            WHERE id = ?
        """, (status, completed_at, item_id))
    else:
        cursor.execute("""
            UPDATE items 
            SET status = ?
            WHERE id = ?
        """, (status, item_id))
    conn.commit()


def update_item(item_id, title=None, assigned_to=None, priority=None, 
                budget=None, purchase_link=None, notes=None):
    """Update item fields"""
    updates = []
    values = []
    
    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if assigned_to is not None:
        updates.append("assigned_to = ?")
        values.append(assigned_to)
    if priority is not None:
        updates.append("priority = ?")
        values.append(priority)
    if budget is not None:
        updates.append("budget = ?")
        values.append(budget)
    if purchase_link is not None:
        updates.append("purchase_link = ?")
        values.append(purchase_link)
    if notes is not None:
        updates.append("notes = ?")
        values.append(notes)
    
    if updates:
        values.append(item_id)
        query = f"UPDATE items SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()


def delete_item(item_id):
    """Delete an item from database"""
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()


def mark_completed(item_id):
    """Mark an item as completed"""
    update_item_status(item_id, 'COMPLETED')


def archive_old_completed_items(days=30):
    """Archive items completed more than X days ago"""
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    cursor.execute("""
        UPDATE items 
        SET status = 'ARCHIVED'
        WHERE status = 'COMPLETED' AND completed_at < ?
    """, (cutoff_date,))
    conn.commit()


def get_dashboard_metrics():
    """Get metrics for dashboard"""
    metrics = {}
    
    # Pending tasks (TODO + IN_PROGRESS)
    cursor.execute("""
        SELECT COUNT(*) FROM items 
        WHERE item_type = 'TASK' AND status IN ('TODO', 'IN_PROGRESS')
    """)
    metrics['pending_tasks'] = cursor.fetchone()[0]
    
    # Tasks in progress
    cursor.execute("""
        SELECT COUNT(*) FROM items 
        WHERE item_type = 'TASK' AND status = 'IN_PROGRESS'
    """)
    metrics['tasks_in_progress'] = cursor.fetchone()[0]
    
    # Pending purchases
    cursor.execute("""
        SELECT COUNT(*) FROM items 
        WHERE item_type = 'PURCHASE' AND status != 'COMPLETED' AND status != 'ARCHIVED'
    """)
    metrics['pending_purchases'] = cursor.fetchone()[0]
    
    # Pending groceries
    cursor.execute("""
        SELECT COUNT(*) FROM items 
        WHERE item_type = 'GROCERY' AND status = 'TODO'
    """)
    metrics['pending_groceries'] = cursor.fetchone()[0]
    
    # Completed this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute("""
        SELECT COUNT(*) FROM items 
        WHERE status = 'COMPLETED' AND completed_at >= ?
    """, (first_day_of_month,))
    metrics['completed_this_month'] = cursor.fetchone()[0]
    
    return metrics


def get_recent_completed(limit=10):
    """Get recently completed items"""
    cursor.execute("""
        SELECT * FROM items 
        WHERE status = 'COMPLETED'
        ORDER BY completed_at DESC
        LIMIT ?
    """, (limit,))
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_archived_items(item_type=None):
    """Get archived items, optionally filtered by type"""
    if item_type:
        cursor.execute("""
            SELECT * FROM items 
            WHERE status = 'ARCHIVED' AND item_type = ?
            ORDER BY completed_at DESC
        """, (item_type,))
    else:
        cursor.execute("""
            SELECT * FROM items 
            WHERE status = 'ARCHIVED' OR status = 'COMPLETED'
            ORDER BY completed_at DESC, created_at DESC
        """)
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Initialize database on import
init_db()
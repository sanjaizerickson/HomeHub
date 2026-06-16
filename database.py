"""
Database module with PostgreSQL support for production and SQLite for local dev
"""
import os
from datetime import datetime, timedelta, timezone

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    """Get current time in IST"""
    return datetime.now(IST)

# Determine which database to use
# Try Streamlit secrets first, then fall back to environment variable
try:
    import streamlit as st
    DATABASE_URL = st.secrets.get("DATABASE_URL", None)
except:
    DATABASE_URL = os.environ.get('DATABASE_URL')

USE_POSTGRES = DATABASE_URL is not None and DATABASE_URL != ""

# Track if database has been initialized
_db_initialized = False

if USE_POSTGRES:
    # PostgreSQL setup
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_connection():
        """Get PostgreSQL connection"""
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
else:
    # SQLite setup (for local development)
    import sqlite3
    
    _sqlite_conn = None
    
    def get_connection():
        """Get SQLite connection"""
        global _sqlite_conn
        if _sqlite_conn is None:
            _sqlite_conn = sqlite3.connect("data.db", check_same_thread=False)
        return _sqlite_conn


def migrate_db():
    """Migrate existing database to add missing columns (SQLite only)"""
    if USE_POSTGRES:
        return  # PostgreSQL migrations handled separately
    
    conn = get_connection()
    cursor = conn.cursor()
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
    global _db_initialized
    
    if _db_initialized:
        return  # Already initialized
    
    try:
        if USE_POSTGRES:
            # PostgreSQL initialization
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS items(
                id SERIAL PRIMARY KEY,
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
            cursor.close()
            conn.close()
        else:
            # SQLite initialization
            conn = get_connection()
            cursor = conn.cursor()
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
        
        _db_initialized = True
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        # Don't crash - let operations fail individually with better error messages


def create_item(title, item_type, status, assigned_to=None, priority=None, 
                budget=None, purchase_link=None, notes=None):
    """Create a new item in the database"""
    ensure_db_initialized()
    created_at = get_ist_now().isoformat()
    
    connection = get_connection()
    cursor = connection.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            INSERT INTO items (title, item_type, status, assigned_to, priority, 
                              budget, purchase_link, notes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (title, item_type, status, assigned_to, priority, budget, purchase_link, notes, created_at))
        item_id = cursor.fetchone()['id']
        connection.commit()
        cursor.close()
        connection.close()
    else:
        cursor.execute("""
            INSERT INTO items (title, item_type, status, assigned_to, priority, 
                              budget, purchase_link, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, item_type, status, assigned_to, priority, budget, purchase_link, notes, created_at))
        connection.commit()
        item_id = cursor.lastrowid
    
    return item_id


def get_all_items():
    """Get all items from database"""
    ensure_db_initialized()
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
    
    if USE_POSTGRES:
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items
    else:
        columns = [description[0] for description in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return items


def get_items_by_type(item_type, exclude_archived=True):
    """Get items filtered by type"""
    ensure_db_initialized()
    connection = get_connection()
    cursor = connection.cursor()
    
    if exclude_archived:
        if USE_POSTGRES:
            cursor.execute("""
                SELECT * FROM items 
                WHERE item_type = %s AND status != 'ARCHIVED'
                ORDER BY created_at DESC
            """, (item_type,))
        else:
            cursor.execute("""
                SELECT * FROM items 
                WHERE item_type = ? AND status != 'ARCHIVED'
                ORDER BY created_at DESC
            """, (item_type,))
    else:
        if USE_POSTGRES:
            cursor.execute("""
                SELECT * FROM items 
                WHERE item_type = %s
                ORDER BY created_at DESC
            """, (item_type,))
        else:
            cursor.execute("""
                SELECT * FROM items 
                WHERE item_type = ?
                ORDER BY created_at DESC
            """, (item_type,))
    
    if USE_POSTGRES:
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items
    else:
        columns = [description[0] for description in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return items


def get_item_counts():
    """Get counts of different item types by status"""
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT item_type, status, COUNT(*) as count
        FROM items
        WHERE status != 'ARCHIVED' AND status != 'COMPLETED'
        GROUP BY item_type, status
    """)
    
    if USE_POSTGRES:
        counts = cursor.fetchall()
        cursor.close()
        connection.close()
        return counts
    else:
        return cursor.fetchall()


def update_item_status(item_id, status):
    """Update item status and set completed_at if status is COMPLETED"""
    completed_at = get_ist_now().isoformat() if status == 'COMPLETED' else None
    
    connection = get_connection()
    cursor = connection.cursor()
    
    if status == 'COMPLETED':
        if USE_POSTGRES:
            cursor.execute("""
                UPDATE items 
                SET status = %s, completed_at = %s
                WHERE id = %s
            """, (status, completed_at, item_id))
        else:
            cursor.execute("""
                UPDATE items 
                SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status, completed_at, item_id))
    else:
        if USE_POSTGRES:
            cursor.execute("""
                UPDATE items 
                SET status = %s
                WHERE id = %s
            """, (status, item_id))
        else:
            cursor.execute("""
                UPDATE items 
                SET status = ?
                WHERE id = ?
            """, (status, item_id))
    
    connection.commit()
    
    if USE_POSTGRES:
        cursor.close()
        connection.close()


def update_item(item_id, title=None, assigned_to=None, priority=None, 
                budget=None, purchase_link=None, notes=None):
    """Update item fields"""
    updates = []
    values = []
    
    if title is not None:
        updates.append("title = " + ("%s" if USE_POSTGRES else "?"))
        values.append(title)
    if assigned_to is not None:
        updates.append("assigned_to = " + ("%s" if USE_POSTGRES else "?"))
        values.append(assigned_to)
    if priority is not None:
        updates.append("priority = " + ("%s" if USE_POSTGRES else "?"))
        values.append(priority)
    if budget is not None:
        updates.append("budget = " + ("%s" if USE_POSTGRES else "?"))
        values.append(budget)
    if purchase_link is not None:
        updates.append("purchase_link = " + ("%s" if USE_POSTGRES else "?"))
        values.append(purchase_link)
    if notes is not None:
        updates.append("notes = " + ("%s" if USE_POSTGRES else "?"))
        values.append(notes)
    
    if updates:
        values.append(item_id)
        query = f"UPDATE items SET {', '.join(updates)} WHERE id = " + ("%s" if USE_POSTGRES else "?")
        
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        
        if USE_POSTGRES:
            cursor.close()
            connection.close()


def delete_item(item_id):
    """Delete an item from database"""
    connection = get_connection()
    cursor = connection.cursor()
    
    if USE_POSTGRES:
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    else:
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    
    connection.commit()
    
    if USE_POSTGRES:
        cursor.close()
        connection.close()


def mark_completed(item_id):
    """Mark an item as completed"""
    update_item_status(item_id, 'COMPLETED')


def archive_old_completed_items(days=30):
    """Archive items completed more than X days ago"""
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    connection = get_connection()
    cursor = connection.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            UPDATE items 
            SET status = 'ARCHIVED'
            WHERE status = 'COMPLETED' AND completed_at < %s
        """, (cutoff_date,))
    else:
        cursor.execute("""
            UPDATE items 
            SET status = 'ARCHIVED'
            WHERE status = 'COMPLETED' AND completed_at < ?
        """, (cutoff_date,))
    
    connection.commit()
    
    if USE_POSTGRES:
        cursor.close()
        connection.close()


def get_dashboard_metrics():
    """Get metrics for dashboard"""
    ensure_db_initialized()
    metrics = {}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    # TASKS - Completed vs Total
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK' AND status = 'COMPLETED'
    """)
    result = cursor.fetchone()
    metrics['tasks_completed'] = result['count'] if USE_POSTGRES else result[0]
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK'
    """)
    result = cursor.fetchone()
    metrics['tasks_total'] = result['count'] if USE_POSTGRES else result[0]
    
    # SHOPPING - Delivered vs Total
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'PURCHASE' AND (status = 'DELIVERED' OR status = 'COMPLETED')
    """)
    result = cursor.fetchone()
    metrics['shopping_completed'] = result['count'] if USE_POSTGRES else result[0]
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'PURCHASE'
    """)
    result = cursor.fetchone()
    metrics['shopping_total'] = result['count'] if USE_POSTGRES else result[0]
    
    # GROCERIES - Completed vs Total
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'GROCERY' AND status = 'COMPLETED'
    """)
    result = cursor.fetchone()
    metrics['groceries_completed'] = result['count'] if USE_POSTGRES else result[0]
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'GROCERY'
    """)
    result = cursor.fetchone()
    metrics['groceries_total'] = result['count'] if USE_POSTGRES else result[0]
    
    # Calculate overall completion percentage
    total_items = metrics['tasks_total'] + metrics['shopping_total'] + metrics['groceries_total']
    completed_items = metrics['tasks_completed'] + metrics['shopping_completed'] + metrics['groceries_completed']
    metrics['overall_completion'] = (completed_items / total_items * 100) if total_items > 0 else 0
    
    # Pending tasks (TODO + IN_PROGRESS) - kept for backward compatibility
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK' AND status IN ('TODO', 'IN_PROGRESS')
    """)
    result = cursor.fetchone()
    metrics['pending_tasks'] = result['count'] if USE_POSTGRES else result[0]
    
    # Tasks in progress - kept for backward compatibility
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK' AND status = 'IN_PROGRESS'
    """)
    result = cursor.fetchone()
    metrics['tasks_in_progress'] = result['count'] if USE_POSTGRES else result[0]
    
    # Pending purchases - kept for backward compatibility
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'PURCHASE' AND status != 'COMPLETED' AND status != 'ARCHIVED'
    """)
    result = cursor.fetchone()
    metrics['pending_purchases'] = result['count'] if USE_POSTGRES else result[0]
    
    # Pending groceries - kept for backward compatibility
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'GROCERY' AND status = 'TODO'
    """)
    result = cursor.fetchone()
    metrics['pending_groceries'] = result['count'] if USE_POSTGRES else result[0]
    
    # Completed this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    if USE_POSTGRES:
        cursor.execute("""
            SELECT COUNT(*) as count FROM items 
            WHERE status = 'COMPLETED' AND completed_at >= %s
        """, (first_day_of_month,))
    else:
        cursor.execute("""
            SELECT COUNT(*) as count FROM items 
            WHERE status = 'COMPLETED' AND completed_at >= ?
        """, (first_day_of_month,))
    
    result = cursor.fetchone()
    metrics['completed_this_month'] = result['count'] if USE_POSTGRES else result[0]
    
    if USE_POSTGRES:
        cursor.close()
        connection.close()
    
    return metrics


def get_recent_completed(limit=10):
    """Get recently completed items"""
    connection = get_connection()
    cursor = connection.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            SELECT * FROM items 
            WHERE status = 'COMPLETED'
            ORDER BY completed_at DESC
            LIMIT %s
        """, (limit,))
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items
    else:
        cursor.execute("""
            SELECT * FROM items 
            WHERE status = 'COMPLETED'
            ORDER BY completed_at DESC
            LIMIT ?
        """, (limit,))
        columns = [description[0] for description in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return items


def get_archived_items(item_type=None):
    """Get archived items, optionally filtered by type"""
    connection = get_connection()
    cursor = connection.cursor()
    
    if item_type:
        if USE_POSTGRES:
            cursor.execute("""
                SELECT * FROM items 
                WHERE status = 'ARCHIVED' AND item_type = %s
                ORDER BY completed_at DESC
            """, (item_type,))
        else:
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
    
    if USE_POSTGRES:
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items
    else:
        columns = [description[0] for description in cursor.description]
        items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return items


def ensure_db_initialized():
    """Ensure database is initialized before operations"""
    if not _db_initialized:
        init_db()


# Don't initialize at import time - do it lazily on first operation
# This prevents crashes when DATABASE_URL is not yet available

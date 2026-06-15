"""
Database module with PostgreSQL support for production and SQLite for local dev
"""
import os
from datetime import datetime, timedelta

# Determine which database to use
DATABASE_URL = os.environ.get('DATABASE_URL')  # PostgreSQL connection string from Streamlit secrets
USE_POSTGRES = DATABASE_URL is not None

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
    
    conn = sqlite3.connect("data.db", check_same_thread=False)
    
    def get_connection():
        """Get SQLite connection"""
        return conn


def migrate_db():
    """Migrate existing database to add missing columns (SQLite only)"""
    if USE_POSTGRES:
        return  # PostgreSQL migrations handled separately
    
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


def create_item(title, item_type, status, assigned_to=None, priority=None, 
                budget=None, purchase_link=None, notes=None):
    """Create a new item in the database"""
    created_at = datetime.now().isoformat()
    
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
    completed_at = datetime.now().isoformat() if status == 'COMPLETED' else None
    
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
    metrics = {}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    # Pending tasks (TODO + IN_PROGRESS)
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK' AND status IN ('TODO', 'IN_PROGRESS')
    """)
    result = cursor.fetchone()
    metrics['pending_tasks'] = result['count'] if USE_POSTGRES else result[0]
    
    # Tasks in progress
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'TASK' AND status = 'IN_PROGRESS'
    """)
    result = cursor.fetchone()
    metrics['tasks_in_progress'] = result['count'] if USE_POSTGRES else result[0]
    
    # Pending purchases
    cursor.execute("""
        SELECT COUNT(*) as count FROM items 
        WHERE item_type = 'PURCHASE' AND status != 'COMPLETED' AND status != 'ARCHIVED'
    """)
    result = cursor.fetchone()
    metrics['pending_purchases'] = result['count'] if USE_POSTGRES else result[0]
    
    # Pending groceries
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


# Initialize database on module import
init_db()

"""
Debug script to test Streamlit secrets and database connection
Run with: streamlit run debug_streamlit.py
"""
import streamlit as st

st.title("🔍 Database Connection Debug")

# Check if secrets are loaded
st.subheader("1. Check Secrets")
try:
    if "DATABASE_URL" in st.secrets:
        db_url = st.secrets["DATABASE_URL"]
        # Mask password
        if "@" in db_url:
            parts = db_url.split("@")
            masked = parts[0].split(":")[0] + ":***@" + "@".join(parts[1:])
            st.success(f"✅ DATABASE_URL found in secrets")
            st.code(masked)
        else:
            st.success(f"✅ DATABASE_URL found but format looks wrong")
            st.code(db_url)
    else:
        st.error("❌ DATABASE_URL not found in st.secrets")
        st.write("Available secrets:", list(st.secrets.keys()))
except Exception as e:
    st.error(f"❌ Error reading secrets: {e}")

# Test PostgreSQL import
st.subheader("2. Check psycopg2")
try:
    import psycopg2
    st.success("✅ psycopg2 imported successfully")
except ImportError as e:
    st.error(f"❌ Failed to import psycopg2: {e}")

# Test connection
st.subheader("3. Test Database Connection")
if st.button("Test Connection"):
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        db_url = st.secrets.get("DATABASE_URL")
        
        with st.spinner("Connecting..."):
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            # Test query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            st.success("✅ Connection successful!")
            st.write("PostgreSQL version:", version['version'][:80])
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'items'
                );
            """)
            table_exists = cursor.fetchone()['exists']
            
            if table_exists:
                st.info("✅ 'items' table exists")
                
                # Count items
                cursor.execute("SELECT COUNT(*) as count FROM items;")
                count = cursor.fetchone()['count']
                st.write(f"Total items: {count}")
            else:
                st.warning("⚠️ 'items' table doesn't exist yet")
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        st.error(f"❌ Connection failed!")
        st.exception(e)
        
        # Show detailed error
        import traceback
        st.code(traceback.format_exc())

# Show database.py detection logic
st.subheader("4. Database Module Detection")
try:
    import database
    st.success(f"✅ Database module loaded")
    st.write(f"Using PostgreSQL: {database.USE_POSTGRES}")
    st.write(f"DATABASE_URL set: {database.DATABASE_URL is not None}")
except Exception as e:
    st.error(f"❌ Failed to import database module: {e}")
    st.exception(e)

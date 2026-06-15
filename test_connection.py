"""
Test PostgreSQL connection to Supabase
"""
import os

print("=" * 50)
print("DATABASE CONNECTION TEST")
print("=" * 50)

# Check if DATABASE_URL is set
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    print("✅ DATABASE_URL found!")
    # Hide password in output
    safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"   Connecting to: ...@{safe_url}")
    
    try:
        import psycopg2
        print("✅ psycopg2 module found!")
        
        # Test connection
        print("\n🔌 Testing connection...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Connection successful!")
        print(f"   PostgreSQL version: {version[0][:50]}...")
        
        # Check if items table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'items'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ 'items' table exists!")
            
            # Count items
            cursor.execute("SELECT COUNT(*) FROM items;")
            count = cursor.fetchone()[0]
            print(f"   Total items in database: {count}")
        else:
            print("⚠️  'items' table doesn't exist yet (will be created on first use)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        
    except ImportError:
        print("❌ psycopg2 not installed!")
        print("   Run: pip install psycopg2-binary")
        
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print("\n💡 Check:")
        print("   1. Password in DATABASE_URL is correct")
        print("   2. Network connection is working")
        print("   3. Supabase project is active")
else:
    print("❌ DATABASE_URL not found!")
    print("\n💡 Set it with:")
    print('   $env:DATABASE_URL="your-connection-string"')
    print("\n   Then restart your terminal/VS Code")

print()

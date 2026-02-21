import os
import psycopg2
from dotenv import load_dotenv

def test_connection():
    """
    Simple script to verify database connectivity and basic SELECT functionality.
    """
    load_dotenv()
    db_url = os.getenv("POSTGRES_URL")
    
    # Matching the fix in init_db.py if localhost is used
    if db_url:
        db_url = db_url.replace("localhost", "127.0.0.1")

    print(f"Testing connection to: {db_url.split('@')[-1] if db_url else 'None'}")
    
    try:
        # 1. Attempt connection
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        print("✅ Successfully connected to the database.")

        # 2. Check for public tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [r[0] for r in cur.fetchall()]
        
        if tables:
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
            
            # 3. Try to query the first table found (limit 1)
            target_table = tables[0]
            print(f"Attempting to query 1 row from '{target_table}'...")
            cur.execute(f"SELECT * FROM {target_table} LIMIT 1;")
            row = cur.fetchone()
            
            if row:
                print(f"✅ Query successful! Sample data: {row}")
            else:
                print(f"⚠️ Query successful, but the table '{target_table}' is empty.")
        else:
            print("❌ No tables found in the 'public' schema. Did you run init_db.py?")

        cur.close()
        conn.close()
        print("\nConnection test passed!")

    except Exception as e:
        print(f"\n❌ Connection test failed!")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()

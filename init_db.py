import os
import psycopg2
from dotenv import load_dotenv

def init_db():
    load_dotenv()
    db_url = os.getenv("POSTGRES_URL")
    if db_url:
        db_url = db_url.replace("localhost", "127.0.0.1")
    
    if not db_url or "user:password" in db_url:
        print("Error: Please update POSTGRES_URL in your .env file with real credentials.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print(f"Connecting to database to initialize schema...")
        
        sql_path = os.path.join(os.path.dirname(__file__), "setup_db.sql")
        with open(sql_path, "r") as f:
            sql_script = f.read()
        
        cur.execute(sql_script)
        conn.commit()
        
        print("Database initialized and seeded successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()

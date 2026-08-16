import sqlite3
import database

DB_NAME = "eco_buddy.db"

def migrate():
    # 1. Initialize users table
    database.init_db()
    
    # 2. Add user_id to assessments if it doesn't exist
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if user_id exists
        cursor.execute("PRAGMA table_info(assessments)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "user_id" not in columns:
            print("Adding user_id column to assessments table...")
            cursor.execute("ALTER TABLE assessments ADD COLUMN user_id INTEGER DEFAULT 1")
            conn.commit()
            print("Migration successful.")
        else:
            print("user_id already exists in assessments.")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()

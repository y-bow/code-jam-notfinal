import sqlite3
import os

db_path = 'instance/app.db'
if not os.path.exists(db_path):
    # Try different path if not in instance/
    db_path = 'app.db'

print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'sgpa' not in columns:
        print("Adding sgpa column to students table...")
        cursor.execute("ALTER TABLE students ADD COLUMN sgpa FLOAT DEFAULT 0.0")
        conn.commit()
        print("Column added successfully.")
    else:
        print("sgpa column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")

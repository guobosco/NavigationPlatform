import sqlite3
import os

# Use the correct database name
db_path = "backend/data/starbase.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}, checking absolute path...")
    # Try absolute path logic similar to database.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    db_path = os.path.join(DATA_DIR, "starbase.db")
    if not os.path.exists(db_path):
        print(f"Database still not found at {db_path}, exiting.")
        exit()

print(f"Migrating database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, column, type_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding column {column}: {e}")

# Add new columns to apps table
add_column("apps", "sort_order", "INTEGER DEFAULT 0")
add_column("apps", "is_pinned", "BOOLEAN DEFAULT 0")
add_column("apps", "is_starred", "BOOLEAN DEFAULT 0")
add_column("apps", "visits", "INTEGER DEFAULT 0")

conn.commit()
conn.close()
print("Migration completed successfully.")

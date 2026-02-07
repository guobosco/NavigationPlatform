import sqlite3
import os

db_path = "backend/data/sql_app.db"

if not os.path.exists(db_path):
    print("Database not found, skipping migration.")
    exit()

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

conn.commit()
conn.close()
print("Migration completed.")

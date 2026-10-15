import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent /"database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREAT TABLE IF NOT EXISTS items
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        description TEXT
        
        """)



















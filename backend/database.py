import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("books.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return  conn

def create_database():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXIST authors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXTNOT NULL UNIQUE
        )
        """)
        conn.execute("""CREATE TABLE IF NOT EXISTS books(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT  NOT NULL,
         author_id INTEGER NOT NULL,
         book_link TEXT,
         genres text,
         average_rating REAL,
         published_year INTEGER
         FOREIGN KEY (author_id) REFERENCES  authors(id),
         UNIQUE (title, author_id)
         )
        """)

def insert_data(books,authors):
    create_database()
    with get_connection() as conn:
        for author in authors :
            coon.execute("INSERT OR INTO authors (name) VALUES(?)"(author,))
        for (titles,authors),info in books.items():
            conn.execute("INSSERT OR IGNORE INTO authors (name) VALUES (?) " (author,))
            author_id = conn.execute(
                "SELECT id FROM authors WHERE NAME = ?"(author,)
            ).fetchall()["id"]
            conn.execute("""
            INSERT OR IGNORE INTO books
            (title,author_id,book_link,genres) 
            """)




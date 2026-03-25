import sqlite3
import os

def get_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "parking.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parking (
            id INTEGER PRIMARY KEY,
            plate TEXT
        )
    """)

    # Opret 18 pladser hvis de ikke findes
    for i in range(1, 19):
        conn.execute("INSERT OR IGNORE INTO parking (id, plate) VALUES (?, NULL)", (i,))
    conn.commit()
    conn.close()
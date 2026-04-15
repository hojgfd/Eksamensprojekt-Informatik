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

    #parking revervation table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parking (
            id INTEGER PRIMARY KEY,
            plate TEXT,
            date TEXT,
            user_id INTEGER
        )
    """)

    #live parking data table
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS liveparkingdata
                 (
                     id INTEGER PRIMARY KEY,
                     spots_left INTEGER,
                     spots_taken INTEGER
                 )
                 """)

    #account table
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS users
                 (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE,
                     password TEXT,
                     address TEXT UNIQUE,
                     distance INTEGER UNIQUE,
                     plate TEXT UNIQUE
                 )
                 """)

    # Opret 18 pladser hvis de ikke findes
    for i in range(1, 19):
        conn.execute(
            "INSERT OR IGNORE INTO parking (id, plate, date) VALUES (?, NULL, NULL)",
            (i,)
        )

    # indsæt et element i live data tabellen
    conn.execute("INSERT OR IGNORE INTO liveparkingdata (id, spots_left, spots_taken) VALUES (0, NULL, NULL)")
    conn.commit()
    conn.close()
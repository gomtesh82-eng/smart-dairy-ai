import sqlite3
import os

def create_table():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'dairy.db')

    os.makedirs(os.path.join(BASE_DIR, '..', 'database'), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Milk table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS milk_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id TEXT,
            date TEXT,
            shift TEXT,
            qty REAL,
            fat REAL,
            snf REAL
        )
    ''')

    # User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Default user
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                   ("admin", "admin123"))

    conn.commit()
    conn.close()

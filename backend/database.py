import sqlite3

def create_table():
    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

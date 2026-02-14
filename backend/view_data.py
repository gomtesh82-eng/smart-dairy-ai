import sqlite3

conn = sqlite3.connect('dairy.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM milk")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

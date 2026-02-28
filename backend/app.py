from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smartdairysecret"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("dairy.db")
    c = conn.cursor()

    # Farmer Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS farmer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        village TEXT
    )
    """)

    # Milk Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS milk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        animal_type TEXT,
        date TEXT,
        session TEXT,
        quantity REAL,
        fat REAL,
        snf REAL,
        rate REAL,
        total REAL,
        FOREIGN KEY (farmer_id) REFERENCES farmer(id)
    )
    """)

    # Insert default farmers if table empty
    c.execute("SELECT COUNT(*) FROM farmer")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO farmer (name) VALUES (?)", ("Ramesh",))
        c.execute("INSERT INTO farmer (name) VALUES (?)", ("Suresh",))

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME (DASHBOARD) ----------------
@app.route('/')
def home():
    conn = sqlite3.connect("dairy.db")
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # Cow Data
    c.execute("""
        SELECT SUM(quantity), SUM(total)
        FROM milk
        WHERE date=? AND animal_type='Cow'
    """, (today,))
    cow = c.fetchone()
    cow_qty = cow[0] or 0
    cow_amount = cow[1] or 0

    # Buffalo Data
    c.execute("""
        SELECT SUM(quantity), SUM(total)
        FROM milk
        WHERE date=? AND animal_type='Buffalo'
    """, (today,))
    buffalo = c.fetchone()
    buffalo_qty = buffalo[0] or 0
    buffalo_amount = buffalo[1] or 0

    conn.close()

    return render_template("index.html",
                           cow_qty=cow_qty,
                           cow_amount=cow_amount,
                           buffalo_qty=buffalo_qty,
                           buffalo_amount=buffalo_amount)

# ---------------- FARMER ----------------
@app.route('/farmers', methods=['GET', 'POST'])
def farmers():
    conn = sqlite3.connect("dairy.db")
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        village = request.form['village']

        c.execute(
            "INSERT INTO farmer (name, mobile, village) VALUES (?,?,?)",
            (name, mobile, village)
        )
        conn.commit()
        return redirect('/farmers')

    c.execute("SELECT * FROM farmer")
    data = c.fetchall()
    conn.close()

    return render_template("farmers.html", farmers=data)

# ---------------- MILK ENTRY ----------------
@app.route('/add_milk', methods=['GET', 'POST'])
def add_milk():

    conn = sqlite3.connect("dairy.db")
    c = conn.cursor()

    c.execute("SELECT * FROM farmer")
    farmers = c.fetchall()

    if request.method == 'POST':

        farmer_id = request.form['farmer_id']
        animal_type = request.form['animal_type']
        date = request.form['date']
        session = request.form['shift']
        quantity = float(request.form['quantity'])
        fat = float(request.form['fat'])
        snf = float(request.form['snf'])

        # Rate Formula
        rate = round((fat * 2.7) + (snf * 3), 2)
        total = round(quantity * rate, 2)

        c.execute("""
        INSERT INTO milk 
        (farmer_id, animal_type, date, session, quantity, fat, snf, rate, total)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (farmer_id, animal_type, date, session,
              quantity, fat, snf, rate, total))

        conn.commit()
        conn.close()
        return redirect('/add_milk')

    conn.close()
    return render_template("add_milk.html", farmers=farmers)

# ---------------- REPORT ----------------
@app.route('/report')
def report():
    conn = sqlite3.connect("dairy.db")
    c = conn.cursor()

    # Cow Data
    c.execute("""
    SELECT milk.id, farmer.name, milk.date, milk.session,
           milk.quantity, milk.fat, milk.snf, milk.total
    FROM milk
    JOIN farmer ON milk.farmer_id = farmer.id
    WHERE animal_type = 'Cow'
    ORDER BY milk.date DESC
    """)
    cow_data = c.fetchall()

    # Buffalo Data
    c.execute("""
    SELECT milk.id, farmer.name, milk.date, milk.session,
           milk.quantity, milk.fat, milk.snf, milk.total
    FROM milk
    JOIN farmer ON milk.farmer_id = farmer.id
    WHERE animal_type = 'Buffalo'
    ORDER BY milk.date DESC
    """)
    buffalo_data = c.fetchall()

    conn.close()

    return render_template("report.html",
                           cow_data=cow_data,
                           buffalo_data=buffalo_data)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
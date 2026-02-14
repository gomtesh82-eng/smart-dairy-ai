from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from database import create_table
from datetime import date

app = Flask(__name__)

# Create database & table when server starts
create_table()


# ---------------- Dashboard ----------------
@app.route('/')
def dashboard():
    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()

    today = str(date.today())   # Format: YYYY-MM-DD

    # Get today's total milk
    cursor.execute("SELECT SUM(qty) FROM milk_data WHERE date = ?", (today,))
    result = cursor.fetchone()[0]

    conn.close()

    # Handle None
    today_milk = result if result else 0

    # Income calculation
    today_income = today_milk * 45
    total_animals = 4

    # Milk status logic
    if today_milk < 12:
        milk_status = "Milk Decreased"
        status_color = "red"
    elif today_milk <= 14:
        milk_status = "Milk Moderate"
        status_color = "orange"
    else:
        milk_status = "Milk Increased"
        status_color = "green"

    return render_template(
        'dashboard.html',
        today_milk=today_milk,
        today_income=today_income,
        total_animals=total_animals,
        milk_status=milk_status,
        status_color=status_color
    )


# ---------------- Milk Entry Page ----------------
@app.route('/milkentry')
def milkentry():
    return render_template('milkentry.html')


# ---------------- Save Milk Data ----------------
@app.route('/submit_milk', methods=['POST'])
def submit_milk():
    animal_id = request.form['animal_id']
    date_value = request.form['date']
    shift = request.form['shift']
    qty = float(request.form['qty'])
    fat = float(request.form['fat'])
    snf = float(request.form['snf'])

    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO milk_data (animal_id, date, shift, qty, fat, snf)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (animal_id, date_value, shift, qty, fat, snf))

    conn.commit()
    conn.close()

    # Redirect to dashboard after saving
    return redirect(url_for('dashboard'))


# ---------------- View All Data ----------------
@app.route('/view_data')
def view_data():
    conn = sqlite3.connect('dairy.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM milk_data")
    data = cursor.fetchall()

    conn.close()

    return render_template('view_data.html', records=data)


# ---------------- Run Server ----------------
if __name__ == '__main__':
    app.run(debug=True)

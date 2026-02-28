from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from database import create_table
from datetime import date, datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "smartdairy"

# ---------------- Constants ----------------
MILK_RATE = 45

# ---------------- Database Config ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'dairy.db')

create_table()


# ---------------- Helper Functions ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Login Required Decorator (Industry Practice)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session.pop('clear_today', None)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Login"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- Dashboard ----------------
@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    today = str(date.today())

    # ---------------- Today Milk ----------------
    cursor.execute("SELECT SUM(qty) FROM milk_data WHERE date=?", (today,))
    today_milk = cursor.fetchone()[0] or 0
    today_milk = round(today_milk, 2)

    if session.get('clear_today'):
        today_milk = 0

    today_income = today_milk * MILK_RATE

    # ---------------- Last 7 Days Chart ----------------
    cursor.execute("""
        SELECT date, SUM(qty) as total
        FROM milk_data
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    """)
    rows = cursor.fetchall()[::-1]

    dates = [row['date'] for row in rows]
    quantities = [row['total'] for row in rows]

    if not dates:
        dates, quantities = [], []

    # ---------------- Monthly Total ----------------
    current_month = date.today().strftime("%Y-%m")
    cursor.execute("""
        SELECT SUM(qty)
        FROM milk_data
        WHERE date LIKE ?
    """, (current_month + "%",))

    month_milk = cursor.fetchone()[0] or 0
    month_milk = round(month_milk, 2)
    month_income = month_milk * MILK_RATE

    # ---------------- Average Milk Per Day ----------------
    cursor.execute("""
        SELECT COUNT(DISTINCT date), SUM(qty)
        FROM milk_data
    """)
    days, total_milk = cursor.fetchone()
    days = days or 1
    total_milk = total_milk or 0
    avg_milk = round(total_milk / days, 2)

    # ---------------- Yearly Income ----------------
    current_year = date.today().strftime("%Y")
    cursor.execute("""
        SELECT SUM(qty)
        FROM milk_data
        WHERE date LIKE ?
    """, (current_year + "%",))
    year_milk = cursor.fetchone()[0] or 0
    total_income_year = round(year_milk * MILK_RATE, 2)

    # ---------------- Monthly Chart Data (12 months) ----------------
    cursor.execute("""
        SELECT strftime('%m', date) as month, SUM(qty)
        FROM milk_data
        WHERE date LIKE ?
        GROUP BY month
        ORDER BY month
    """, (current_year + "%",))

    month_data = cursor.fetchall()

    month_labels = []
    month_quantities = []

    for row in month_data:
        month_labels.append(row[0])   # 01, 02, etc.
        month_quantities.append(row[1])

    # ---------------- Alerts (Industry Feature) ----------------
    alerts = []
    if today_milk < 10:
        alerts.append({
            "title": "Low Production Alert",
            "message": "Today's milk production is below normal."
        })

    if avg_milk < 12:
        alerts.append({
            "title": "Performance Alert",
            "message": "Average milk production is low."
        })

    # ---------------- Milk Status ----------------
    if today_milk < 10:
        milk_status = "Low Production"
        status_color = "low"
    elif today_milk <= 20:
        milk_status = "Normal Production"
        status_color = "medium"
    else:
        milk_status = "High Production"
        status_color = "high"

    conn.close()

    # ---------------- Render ----------------
    return render_template(
        'dashboard.html',
        today_milk=today_milk,
        today_income=today_income,
        month_milk=month_milk,
        month_income=month_income,
        milk_status=milk_status,
        status_color=status_color,
        dates=dates,
        quantities=quantities,

        # Day 5 additions
        avg_milk=avg_milk,
        total_income_year=total_income_year,
        month_labels=month_labels,
        month_quantities=month_quantities,
        alerts=alerts,
        total_cows=10   # Static for now (you can make animal table later)
    )

# ---------------- Clear Today ----------------
@app.route('/clear_today')
@login_required
def clear_today():
    session['clear_today'] = True
    return redirect(url_for('dashboard'))


# ---------------- Weekly Report ----------------
@app.route('/weekly')
@login_required
def weekly():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, qty FROM milk_data")
    data = cursor.fetchall()
    conn.close()

    weeks = {1: 0, 2: 0, 3: 0, 4: 0}

    for row in data:
        day = int(row['date'].split("-")[2])

        if day <= 7:
            weeks[1] += row['qty']
        elif day <= 14:
            weeks[2] += row['qty']
        elif day <= 21:
            weeks[3] += row['qty']
        else:
            weeks[4] += row['qty']

    income = {w: round(weeks[w] * MILK_RATE, 2) for w in weeks}

    return render_template("weekly.html", weeks=weeks, income=income)


# ---------------- Milk Entry ----------------
@app.route('/milkentry')
@login_required
def milkentry():
    return render_template('milkentry.html')


@app.route('/submit_milk', methods=['POST'])
@login_required
def submit_milk():
    data = (
        request.form['animal_id'],
        request.form['date'],
        request.form['shift'],
        float(request.form['qty']),
        float(request.form['fat']),
        float(request.form['snf'])
    )

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO milk_data (animal_id, date, shift, qty, fat, snf)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


# ---------------- Monthly Report (Industry Format) ----------------
@app.route('/monthly_report')
@login_required
def monthly_report():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, qty FROM milk_data")
    records = cursor.fetchall()
    conn.close()

    # Structure:
    # January
    #    Week1 (1-10)
    #    Week2 (11-20)
    #    Week3 (21-30)
    #    Week4 (31)

    report = {}

    for row in records:
        d = datetime.strptime(row['date'], "%Y-%m-%d")
        qty = row['qty']

        month = d.strftime("%B")
        day = d.day

        if day <= 10:
            week = "Week 1 (1-10)"
        elif day <= 20:
            week = "Week 2 (11-20)"
        elif day <= 30:
            week = "Week 3 (21-30)"
        else:
            week = "Week 4 (31)"

        report.setdefault(month, {})
        report[month].setdefault(week, 0)
        report[month][week] += qty

    # Add Income
    for month in report:
        for week in report[month]:
            milk = report[month][week]
            report[month][week] = {
                "milk": round(milk, 2),
                "income": round(milk * MILK_RATE, 2)
            }

    return render_template("monthly_report.html", report=report)


# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True)

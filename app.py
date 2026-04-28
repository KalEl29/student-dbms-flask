from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Connect Database
def connect_db():
    return sqlite3.connect('database.db')

# Create Tables
def create_table():
    conn = connect_db()
    cur = conn.cursor()

    # Students Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            course TEXT,
            department TEXT,
            admission_year INTEGER
        )
    ''')

    # Attendance Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')

    # Results Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            marks INTEGER,
            grade TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')

    conn.commit()
    conn.close()

create_table()

# Home
@app.route('/')
def index():
    return redirect('/login')

# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO students (name, email, phone, address, course, department, admission_year)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['address'],
            request.form['course'],
            request.form['department'],
            request.form['year']
        ))

        conn.commit()
        conn.close()

        flash("Student added successfully!")
        return redirect('/view')

    return render_template('add_student.html')

# View Students
@app.route('/view')
def view_students():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    return render_template('view_students.html', students=students)

# Edit Student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            UPDATE students
            SET name=?, email=?, phone=?, address=?, course=?, department=?, admission_year=?
            WHERE student_id=?
        """, (
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['address'],
            request.form['course'],
            request.form['department'],
            request.form['year'],
            id
        ))

        conn.commit()
        conn.close()
        flash("Student updated successfully!")
        return redirect('/view')

    cur.execute("SELECT * FROM students WHERE student_id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit_student.html', student=student)

# Delete Student
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id=?", (id,))
    conn.commit()
    conn.close()

    flash("Student deleted successfully!")
    return redirect('/view')

# Add Attendance
@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
        """, (
            request.form['student_id'],
            request.form['date'],
            request.form['status']
        ))

        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template('add_attendance.html')

# View Attendance
@app.route('/view_attendance')
def view_attendance():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.student_id = attendance.student_id
    """)
    data = cur.fetchall()
    conn.close()

    return render_template('view_attendance.html', records=data)

# Add Result
@app.route('/add_result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO results (student_id, subject, marks, grade)
            VALUES (?, ?, ?, ?)
        """, (
            request.form['student_id'],
            request.form['subject'],
            request.form['marks'],
            request.form['grade']
        ))

        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template('add_result.html')

# View Results
@app.route('/view_results')
def view_results():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT students.name, results.subject, results.marks, results.grade
        FROM results
        JOIN students ON students.student_id = results.student_id
    """)
    data = cur.fetchall()
    conn.close()

    return render_template('view_results.html', records=data)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM students 
        WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
    """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))

    data = cur.fetchall()
    conn.close()

    return render_template('view_students.html', students=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            return redirect('/view')
        else:
            flash("Invalid credentials!")

    return render_template('login.html')
# Run App
if __name__ == '__main__':
    app.run(debug=True)
"""Student management routes."""
import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from database import fetch_all, fetch_one, get_connection

students_bp = Blueprint("students", __name__)
GENDERS = ("Male", "Female", "Other")


def valid_student(form):
    code, name = form.get("student_code", "").strip(), form.get("student_name", "").strip()
    gender = form.get("gender", "")
    try:
        class_id = int(form.get("class_id", ""))
    except ValueError:
        return None
    if not code or len(code) > 30 or not name or len(name) > 100 or gender not in GENDERS:
        return None
    if not fetch_one("SELECT ClassID FROM Classes WHERE ClassID=?", class_id):
        return None
    return class_id, code, name, gender


@students_bp.get("/students")
def index():
    term = request.args.get("q", "").strip()
    class_id = request.args.get("class_id", "")
    sql = "SELECT s.StudentID, s.ClassID, s.StudentCode, s.StudentName, s.Gender, c.ClassName FROM Students s JOIN Classes c ON c.ClassID=s.ClassID WHERE (s.StudentName LIKE ? OR s.StudentCode LIKE ?)"
    params = [f"%{term}%", f"%{term}%"]
    if class_id.isdigit():
        sql += " AND s.ClassID=?"
        params.append(int(class_id))
    sql += " ORDER BY c.ClassName, s.StudentName"
    return render_template("students.html", students=fetch_all(sql, params), classes=fetch_all("SELECT ClassID, ClassName FROM Classes ORDER BY ClassName"), q=term, selected_class=class_id, genders=GENDERS)


@students_bp.post("/students")
def create():
    data = valid_student(request.form)
    if not data:
        flash("Enter a valid student code, name, gender, and class.", "danger")
    else:
        try:
            with get_connection() as connection:
                connection.cursor().execute("INSERT INTO Students (ClassID, StudentCode, StudentName, Gender) VALUES (?, ?, ?, ?)", data)
                connection.commit()
            flash("Student added successfully.", "success")
        except sqlite3.IntegrityError:
            flash("That student code already exists.", "danger")
        except sqlite3.Error:
            flash("Could not save the student.", "danger")
    return redirect(url_for("students.index"))


@students_bp.post("/students/<int:student_id>/edit")
def edit(student_id):
    data = valid_student(request.form)
    if not data:
        flash("Enter a valid student code, name, gender, and class.", "danger")
    else:
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Students SET ClassID=?, StudentCode=?, StudentName=?, Gender=? WHERE StudentID=?", (*data, student_id))
                connection.commit()
                flash("Student updated." if cursor.rowcount else "Student not found.", "success" if cursor.rowcount else "warning")
        except sqlite3.IntegrityError:
            flash("That student code already exists.", "danger")
        except sqlite3.Error:
            flash("Could not update the student.", "danger")
    return redirect(url_for("students.index"))


@students_bp.post("/students/<int:student_id>/delete")
def delete(student_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Students WHERE StudentID=?", (student_id,))
            connection.commit()
            flash("Student deleted." if cursor.rowcount else "Student not found.", "success" if cursor.rowcount else "warning")
    except sqlite3.IntegrityError:
        flash("Cannot delete this student while attendance history exists.", "danger")
    except sqlite3.Error:
        flash("Could not delete the student.", "danger")
    return redirect(url_for("students.index"))

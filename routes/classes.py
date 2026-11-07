"""Class management routes."""
import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from database import fetch_all, fetch_one, get_connection

classes_bp = Blueprint("classes", __name__)


@classes_bp.get("/classes")
def index():
    classes = fetch_all("""SELECT c.ClassID, c.ClassName, c.CreatedAt,
        COUNT(s.StudentID) AS StudentCount FROM Classes c
        LEFT JOIN Students s ON s.ClassID=c.ClassID
        GROUP BY c.ClassID, c.ClassName, c.CreatedAt ORDER BY c.ClassName""")
    return render_template("classes.html", classes=classes)


@classes_bp.post("/classes")
def create():
    name = request.form.get("class_name", "").strip()
    if not name or len(name) > 50:
        flash("Class name is required and must be at most 50 characters.", "danger")
    else:
        try:
            with get_connection() as connection:
                connection.cursor().execute("INSERT INTO Classes (ClassName) VALUES (?)", (name,))
                connection.commit()
            flash("Class added successfully.", "success")
        except sqlite3.IntegrityError:
            flash("That class name already exists.", "danger")
        except sqlite3.Error:
            flash("Could not save the class. Check the database connection.", "danger")
    return redirect(url_for("classes.index"))


@classes_bp.post("/classes/<int:class_id>/edit")
def edit(class_id):
    name = request.form.get("class_name", "").strip()
    if not name or len(name) > 50:
        flash("Class name is required and must be at most 50 characters.", "danger")
    else:
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE Classes SET ClassName=? WHERE ClassID=?", (name, class_id))
                connection.commit()
                flash("Class updated." if cursor.rowcount else "Class not found.", "success" if cursor.rowcount else "warning")
        except sqlite3.IntegrityError:
            flash("That class name already exists.", "danger")
        except sqlite3.Error:
            flash("Could not update the class.", "danger")
    return redirect(url_for("classes.index"))


@classes_bp.post("/classes/<int:class_id>/delete")
def delete(class_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Classes WHERE ClassID=? AND NOT EXISTS (SELECT 1 FROM Students WHERE ClassID=?)", (class_id, class_id))
            connection.commit()
            if cursor.rowcount:
                flash("Class deleted.", "success")
            else:
                flash("Class was not deleted. It may contain students or no longer exist.", "warning")
    except sqlite3.Error:
        flash("Could not delete the class.", "danger")
    return redirect(url_for("classes.index"))


@classes_bp.post("/data/delete-all")
def delete_all_data():
    """Clear every attendance, student, and class row in one transaction."""
    if request.form.get("confirm_all") != "yes":
        flash("Confirm the delete-all action before clearing app data.", "danger")
        return redirect(url_for("classes.index"))
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Attendance")
            attendance_count = cursor.rowcount
            cursor.execute("DELETE FROM Students")
            student_count = cursor.rowcount
            cursor.execute("DELETE FROM Classes")
            class_count = cursor.rowcount
        flash(
            f"All app data cleared: {attendance_count} attendance records, "
            f"{student_count} students, and {class_count} classes.",
            "success",
        )
    except sqlite3.Error:
        flash("Could not clear the data. No partial changes were saved.", "danger")
    return redirect(url_for("classes.index"))

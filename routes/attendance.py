"""Attendance entry and history routes."""
from datetime import date
import json
import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for
from database import fetch_all, fetch_one, get_connection

attendance_bp = Blueprint("attendance", __name__)
STATUSES = ("Present", "Permission", "Absent")


@attendance_bp.get("/attendance")
def index():
    classes = fetch_all("SELECT ClassID, ClassName FROM Classes ORDER BY ClassName")
    selected = request.args.get("class_id", "")
    day = request.args.get("date", date.today().isoformat())
    students, saved = [], False
    if selected.isdigit():
        students = fetch_all("""SELECT s.StudentID, s.StudentCode, s.StudentName, s.Gender, a.Status
            FROM Students s LEFT JOIN Attendance a ON a.StudentID=s.StudentID AND a.AttendanceDate=?
            WHERE s.ClassID=? ORDER BY s.StudentName""", (day, int(selected)))
        saved = bool(students) and all(row["Status"] in STATUSES for row in students)
    return render_template("attendance.html", classes=classes, selected_class=selected, attendance_date=day, students=students, saved=saved, statuses=STATUSES)


@attendance_bp.post("/attendance/save")
def save():
    try:
        class_id = int(request.form.get("class_id", ""))
        attendance_date = date.fromisoformat(request.form.get("attendance_date", ""))
        submitted = json.loads(request.form.get("records", "{}"))
        if not isinstance(submitted, dict):
            raise ValueError
    except (ValueError, TypeError, json.JSONDecodeError):
        flash("Choose a valid class and date, then select a status for every student.", "danger")
        return redirect(url_for("attendance.index"))
    if not fetch_one("SELECT ClassID FROM Classes WHERE ClassID=?", class_id):
        flash("Selected class does not exist.", "danger")
        return redirect(url_for("attendance.index"))
    if not submitted or any(status not in STATUSES for status in submitted.values()):
        flash("Select Present, Permission, or Absent for every student before saving.", "danger")
        return redirect(url_for("attendance.index", class_id=class_id, date=attendance_date.isoformat()))
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT StudentID FROM Students WHERE ClassID=?", (class_id,))
            roster = {str(row[0]) for row in cursor.fetchall()}
            if not roster or set(submitted) != roster:
                connection.rollback()
                flash("Attendance must include exactly the current students in this class.", "danger")
                return redirect(url_for("attendance.index", class_id=class_id, date=attendance_date.isoformat()))
            for student_id, status in submitted.items():
                cursor.execute("""INSERT INTO Attendance (StudentID, AttendanceDate, Status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(StudentID, AttendanceDate)
                    DO UPDATE SET Status=excluded.Status""",
                    (int(student_id), attendance_date.isoformat(), status))
            connection.commit()
        flash("Attendance saved successfully.", "success")
    except sqlite3.Error:
        try:
            connection.rollback()
        except (NameError, UnboundLocalError):
            pass
        flash("Attendance could not be saved. No partial changes were kept.", "danger")
    return redirect(url_for("attendance.index", class_id=class_id, date=attendance_date.isoformat()))


@attendance_bp.get("/history")
def history():
    classes = fetch_all("SELECT ClassID, ClassName FROM Classes ORDER BY ClassName")
    day = request.args.get("date", "").strip()
    class_id = request.args.get("class_id", "").strip()
    term = request.args.get("q", "").strip()
    sql = "SELECT a.AttendanceID, a.AttendanceDate, a.Status, s.StudentCode, s.StudentName, c.ClassName, s.StudentID FROM Attendance a JOIN Students s ON s.StudentID=a.StudentID JOIN Classes c ON c.ClassID=s.ClassID WHERE 1=1"
    params = []
    if day:
        sql += " AND a.AttendanceDate=?"
        params.append(day)
    if class_id.isdigit():
        sql += " AND c.ClassID=?"
        params.append(int(class_id))
    if term:
        sql += " AND (s.StudentName LIKE ? OR s.StudentCode LIKE ?)"
        params.extend([f"%{term}%", f"%{term}%"])
    sql += " ORDER BY a.AttendanceDate DESC, c.ClassName, s.StudentName"
    records = fetch_all(sql, params)
    return render_template("history.html", classes=classes, records=records, selected_date=day, selected_class=class_id, q=term)


@attendance_bp.post("/history/<int:attendance_id>/delete")
def delete_history_record(attendance_id):
    """Delete one attendance record from the history."""
    day = request.form.get("date", "").strip()
    class_id = request.form.get("class_id", "").strip()
    term = request.form.get("q", "").strip()
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Attendance WHERE AttendanceID=?", (attendance_id,))
            deleted = cursor.rowcount
        if deleted:
            flash("Attendance history record deleted.", "success")
        else:
            flash("Attendance record was not found.", "warning")
    except sqlite3.Error:
        flash("Could not delete the attendance record.", "danger")
    return redirect(url_for("attendance.history", date=day, class_id=class_id, q=term))


@attendance_bp.post("/history/delete-all")
def delete_all_history():
    """Clear attendance history while preserving students and classes."""
    if request.form.get("confirm_all") != "yes":
        flash("Confirm clearing attendance history before continuing.", "danger")
        return redirect(url_for("attendance.history"))
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Attendance")
            deleted = cursor.rowcount
        flash(f"Cleared {deleted} attendance history record(s). Students and classes were kept.", "success")
    except sqlite3.Error:
        flash("Could not clear attendance history.", "danger")
    return redirect(url_for("attendance.history"))

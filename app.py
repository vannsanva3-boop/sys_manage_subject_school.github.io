"""Student Attendance Management System entry point."""
from datetime import date
from flask import Flask, flash, render_template
from config import Config
from database import fetch_all, init_db
from routes.classes import classes_bp
from routes.students import students_bp
from routes.attendance import attendance_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app.config["DATABASE_PATH"])

    @app.context_processor
    def inject_current_date():
        return {"current_date": date.today().strftime("%A, %d %B %Y")}

    app.register_blueprint(classes_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)

    @app.get("/")
    def home():
        try:
            classes = fetch_all("SELECT ClassID, ClassName FROM Classes ORDER BY ClassName")
        except Exception:
            classes = []
            flash("Cannot open the local SQLite database. Check the database file and folder permissions.", "danger")
        return render_template("attendance.html", classes=classes, selected_class="",
                               attendance_date=date.today().isoformat(), students=[],
                               saved=False, statuses=("Present", "Permission", "Absent"))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", message="The requested page was not found."), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("error.html", message="An unexpected error occurred. Please try again."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

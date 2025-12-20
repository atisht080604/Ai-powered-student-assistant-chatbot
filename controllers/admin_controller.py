# controllers/admin_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import admin_required
from config import ADMIN_USER, ADMIN_PASS
from models.student_model import StudentModel
from models.fee_model import FeeModel
from models.timetable_model import TimetableModel

admin = Blueprint("admin", __name__)

# ------------------------------
# Admin Login
# ------------------------------
@admin.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["is_admin"] = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "error")

    return render_template("admin/admin_login.html")


# ------------------------------
# Admin Dashboard
# ------------------------------
@admin.route("/admin")
@admin_required
def admin_dashboard():
    stats = {
        "students": StudentModel.count(),
        "fees": FeeModel.count(),
        "timetable": TimetableModel.count()
    }
    return render_template("admin/admin_dashboard.html", stats=stats)


# ------------------------------
# Manage Students
# ------------------------------
@admin.route("/admin/students")
@admin_required
def admin_students():
    students = StudentModel.get_all()
    return render_template("admin/admin_students.html", students=students)


@admin.route("/admin/students/add", methods=["POST"])
@admin_required
def admin_students_add():

    success = StudentModel.create(
        roll=request.form.get("roll"),
        name=request.form.get("name"),
        department=request.form.get("department"),
        year=request.form.get("year"),
        email=request.form.get("email"),
        password="1234",
        attendance=request.form.get("attendance")
    )

    if not success:
        flash(
            "⚠️ Student with this roll number already exists. Please use a unique roll number.",
            "error"
        )
        return redirect(url_for("admin.admin_students"))

    flash("✅ Student added successfully!", "success")
    return redirect(url_for("admin.admin_students"))


@admin.route("/admin/students/delete/<int:sid>", methods=["POST"])
@admin_required
def admin_students_delete(sid):
    StudentModel.delete(sid)
    flash("Student deleted!", "info")
    return redirect(url_for("admin.admin_students"))


# -----------------------------------
# Manage Fees
# -----------------------------------
@admin.route("/admin/fees")
@admin_required
def admin_fees():
    fees = FeeModel.get_all()
    return render_template("admin/admin_fees.html", fees=fees)


@admin.route("/admin/fees/add", methods=["POST"])
@admin_required
def admin_fees_add():
    FeeModel.create(
        roll=request.form.get("roll"),
        semester=request.form.get("semester"),
        amount_due=request.form.get("amount_due"),
        amount_paid=request.form.get("amount_paid"),
        due_date=request.form.get("due_date")
    )
    flash("Fee record added!", "success")
    return redirect(url_for("admin.admin_fees"))


@admin.route("/admin/fees/delete/<int:fid>", methods=["POST"])
@admin_required
def admin_fees_delete(fid):
    FeeModel.delete(fid)
    flash("Fee record deleted!", "info")
    return redirect(url_for("admin.admin_fees"))


# -----------------------------------
# Manage Timetable
# -----------------------------------
@admin.route("/admin/timetable")
@admin_required
def admin_timetable():
    rows = TimetableModel.get_all()
    return render_template("admin/admin_timetable.html", timetable=rows)


@admin.route("/admin/timetable/add", methods=["POST"])
@admin_required
def admin_timetable_add():
    TimetableModel.create(
        day=request.form.get("day"),
        class_date=request.form.get("class_date"),
        start_time=request.form.get("start_time"),
        end_time=request.form.get("end_time"),
        subject=request.form.get("subject"),
        instructor=request.form.get("instructor"),
        location=request.form.get("location"),
    )

    flash("Timetable entry added successfully!", "success")
    return redirect(url_for("admin.admin_timetable"))


@admin.route("/admin/timetable/upload", methods=["POST"])
@admin_required
def admin_timetable_upload():
    file = request.files.get("file")

    if not file:
        flash("No file uploaded.", "error")
        return redirect(url_for("admin.admin_timetable"))

    import csv
    from io import TextIOWrapper

    try:
        reader = csv.DictReader(TextIOWrapper(file.stream, encoding="utf-8"))

        for row in reader:
            TimetableModel.create(
                day=row.get("day"),
                start_time=row.get("start_time"),
                end_time=row.get("end_time"),
                subject=row.get("subject"),
                instructor=row.get("instructor"),
                location=row.get("location"),
            )

        flash("CSV uploaded successfully!", "success")

    except Exception as e:
        print("UPLOAD ERROR:", e)
        flash("Error while processing file.", "error")

    return redirect(url_for("admin.admin_timetable"))

@admin.route("/admin/timetable/delete/<int:tid>", methods=["POST"])
@admin_required
def admin_timetable_delete(tid):
    TimetableModel.delete(tid)
    flash("Timetable entry removed successfully!", "info")
    return redirect(url_for("admin.admin_timetable"))


# -----------------------------------
# Admin Logout
# -----------------------------------
@admin.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Admin logged out!", "success")
    return redirect(url_for("admin.admin_login"))

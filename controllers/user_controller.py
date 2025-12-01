# controllers/user_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.student_model import StudentModel

user = Blueprint("user", __name__)

# -------------------------------------
# USER LOGIN
# -------------------------------------
@user.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        roll = request.form.get("roll", "").strip()
        password = request.form.get("password", "").strip()

        student = StudentModel.get_by_roll(roll)

        if student and student.password == password:
            session["user_logged_in"] = True
            session["user_name"] = student.name
            session["user_roll"] = student.roll

            flash(f"Login successful! Welcome back {student.name}", "success")
            return redirect(url_for("main.home"))   # ✔ Correct
        else:
            flash("Invalid credentials.", "error")

    return render_template("user/user_login.html")


# -------------------------------------
# USER REGISTRATION
# -------------------------------------
@user.route("/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        roll = request.form.get("roll")
        name = request.form.get("name")
        dept = request.form.get("department")
        year = request.form.get("year")
        email = request.form.get("email")
        password = request.form.get("password")

        # Basic validation
        if not roll or not name or not password:
            flash("Roll, Name & Password are required", "error")
            return redirect(url_for("user.user_register"))

        # Create user
        StudentModel.create(roll, name, dept, year, email, password)

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("user.user_login"))  # ✔ Correct

    return render_template("user/user_register.html")

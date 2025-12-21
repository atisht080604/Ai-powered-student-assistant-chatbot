from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import user_required
from utils.email_service import send_otp_email
from models.student_model import StudentModel
import random

profile = Blueprint("profile", __name__)

# -------------------------
# VIEW PROFILE (ALIAS FIX ✅)
# -------------------------
@profile.route("/profile/view", methods=["GET"])
@user_required
def view_profile():
    # simply reuse edit_profile logic
    return redirect(url_for("profile.edit_profile"))


# -------------------------
# VIEW / EDIT PROFILE PAGE
# -------------------------
@profile.route("/profile", methods=["GET"])
@user_required
def edit_profile():
    roll = session.get("user_roll")
    student = StudentModel.get_by_roll(roll)
    return render_template("user/edit_profile.html", student=student)


# -------------------------
# SAVE PROFILE CHANGES
# -------------------------
@profile.route("/profile/update", methods=["POST"])
@user_required
def update_profile():
    roll = session.get("user_roll")

    name = request.form.get("name")
    department = request.form.get("department")
    year = request.form.get("year")
    new_email = request.form.get("email")

    student = StudentModel.get_by_roll(roll)

    # 🔴 If email changed → OTP verification
    if new_email != student.email:
        otp = random.randint(100000, 999999)

        session["email_change_otp"] = str(otp)
        session["new_email_temp"] = new_email

        send_otp_email(new_email, otp)

        flash("OTP sent to new email. Please verify.", "info")
        return redirect(url_for("profile.verify_email_otp"))

    # ✅ Normal profile update (without email)
    StudentModel.update_user_profile(
        roll=roll,
        name=name,
        department=department,
        year=year,
        email=student.email
    )

    # Update session values
    session["user_name"] = name

    flash("Profile updated successfully!", "success")
    return redirect(url_for("main.home"))


# -------------------------
# VERIFY OTP FOR EMAIL CHANGE
# -------------------------
@profile.route("/profile/verify_email", methods=["GET", "POST"])
@user_required
def verify_email_otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        if entered_otp == session.get("email_change_otp"):
            roll = session.get("user_roll")
            new_email = session.get("new_email_temp")

            StudentModel.update_email(roll, new_email)

            # Update session email
            session["user_email"] = new_email

            # Clear temp session data
            session.pop("email_change_otp", None)
            session.pop("new_email_temp", None)

            flash("Email updated successfully!", "success")
            return redirect(url_for("profile.edit_profile"))

        else:
            flash("Invalid OTP. Please try again.", "error")

    return render_template("user/verify_email_otp.html")

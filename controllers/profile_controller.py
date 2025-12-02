from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decorators import user_required
from utils.email_service import send_otp_email
from models.student_model import StudentModel
import random

profile = Blueprint("profile", __name__)

# -------------------------
# Edit Profile Page
# -------------------------
@profile.route("/profile", methods=["GET"])
@user_required
def edit_profile():
    roll = session.get("user_roll")
    student = StudentModel.get_by_roll(roll)
    return render_template("user/edit_profile.html", student=student)


# -------------------------
# Save Changes (Except Email)
# -------------------------
@profile.route("/profile/update", methods=["POST"])
@user_required
def update_profile():
    roll = session.get("user_roll")

    name = request.form.get("name")
    year = request.form.get("year")
    new_email = request.form.get("email")

    student = StudentModel.get_by_roll(roll)

    # Check if email changed → Need OTP
    if new_email != student.email:
        otp = random.randint(100000, 999999)
        session["email_change_otp"] = str(otp)
        session["new_email_temp"] = new_email

        send_otp_email(new_email, otp)

        flash("OTP sent to new email!", "info")
        return redirect(url_for("profile.verify_email_otp"))

    # Normal update (no email change)
    StudentModel.update_profile(roll, name, year)
    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile.edit_profile"))


# -------------------------
# Verify OTP for Email Change
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

            # Clear temp session
            session.pop("email_change_otp", None)
            session.pop("new_email_temp", None)

            flash("Email updated successfully!", "success")
            return redirect(url_for("profile.edit_profile"))

        else:
            flash("Invalid OTP!", "error")

    return render_template("user/verify_email_otp.html")

# controllers/otp_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.email_service import send_otp_email
from models.student_model import StudentModel
import random

otp = Blueprint("otp", __name__)

# ------------------------------
# 1. Forgot Password → Enter Email
# ------------------------------
@otp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        user = StudentModel.get_by_email(email)
        if not user:
            flash("Email not found!", "error")
            return redirect(url_for("otp.forgot_password"))

        # Generate OTP
        generated_otp = random.randint(100000, 999999)

        # Save in session
        session["reset_email"] = email
        session["reset_otp"] = str(generated_otp)

        # Send OTP to email
        send_otp_email(email, generated_otp)

        flash("OTP sent to your email!", "success")
        return redirect(url_for("otp.verify_otp"))

    return render_template("otp/forgot.html")


# ------------------------------
# 2. Verify OTP Page
# ------------------------------
@otp.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")

        if "reset_otp" not in session:
            flash("OTP expired! Try again.", "error")
            return redirect(url_for("otp.forgot_password"))

        if entered_otp == session["reset_otp"]:
            flash("OTP verified! Set a new password.", "success")
            return redirect(url_for("otp.reset_password"))
        else:
            flash("Invalid OTP!", "error")

    return render_template("otp/verify_otp.html")


# ------------------------------
# 3. Reset Password
# ------------------------------
@otp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_pass = request.form.get("password")
        email = session.get("reset_email")

        if not email:
            flash("Session expired! Try again.", "error")
            return redirect(url_for("otp.forgot_password"))

        # Update user password
        StudentModel.update_password(email, new_pass)

        # Clear session reset data
        session.pop("reset_email", None)
        session.pop("reset_otp", None)

        flash("Password updated successfully! Please login.", "success")
        return redirect(url_for("user.user_login"))  # FIXED

    return render_template("otp/reset_password.html")

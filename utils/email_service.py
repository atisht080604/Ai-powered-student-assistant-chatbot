# utils/email_service.py
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_USER

import smtplib
import os
from email.message import EmailMessage

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_otp_email(to_email, otp):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Student Assistant - OTP Verification"
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg.set_content(
            f"""
Hello 👋

Your OTP is: {otp}

This OTP is valid for 5 minutes.
Do not share it with anyone.

– Student Assistant
"""
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        print("✅ OTP sent successfully")

    except Exception as e:
        print("❌ OTP ERROR:", e)
        raise

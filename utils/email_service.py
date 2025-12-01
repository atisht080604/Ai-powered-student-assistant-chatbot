# utils/email_service.py
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_APP_PASSWORD

def send_otp_email(to_email: str, otp: int):
    """
    Sends a simple OTP email using Gmail SMTP.
    Make sure:
    - EMAIL_USER is your Gmail
    - EMAIL_APP_PASSWORD is your Google App Password
    """
    sender_email = EMAIL_USER
    password = EMAIL_APP_PASSWORD

    msg = MIMEText(f"Your OTP for password reset is: {otp}")
    msg["Subject"] = "Student Assistant - Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("OTP email sent to:", to_email)
    except Exception as e:
        print("Error sending email:", e)

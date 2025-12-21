# controllers/chat_controller.py
from flask import Blueprint, request, jsonify, session
from models.student_model import StudentModel
from models.fee_model import FeeModel
from models.timetable_model import TimetableModel
from utils.ai_client import client, MODEL
from utils.email_service import send_alert_email
from utils.college_info import COLLEGE_INFO
from utils.local_llm import ask_local_llm
import difflib

chat = Blueprint("chat", __name__)

# -------------------------------
# FUZZY MATCH HELPER
# -------------------------------
def fuzzy_match(word, keywords, threshold=0.75):
    for key in keywords:
        if difflib.SequenceMatcher(None, word, key).ratio() >= threshold:
            return True
    return False


# -------------------------------
# CHAT ROUTE
# -------------------------------
@chat.route("/get_response", methods=["POST"])
def get_response():

    # chat memory
    chat_history = session.get("chat_history", [])

    data = request.get_json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please enter a message."})

    roll = session.get("user_roll")
    if not roll:
        return jsonify({
            "reply": "🔒 Please login to access your academic information."
        })

    msg = user_msg.lower()
    words = msg.split()

    # -------------------------------
    # SECURITY: BLOCK MANUAL ROLL
    # -------------------------------
    if "r0" in msg:
        return jsonify({
            "reply": "🔒 For security reasons, I can only show your own data."
        })

    # -------------------------------
    # 1️⃣ ATTENDANCE
    # -------------------------------
    if any(fuzzy_match(w, ["attendance", "attendence", "attend", "present"], 0.75) for w in words):
        student = StudentModel.get_by_roll(roll)
        return jsonify({
            "reply": f"📊 Your attendance is {student.attendance}%."
        })

    # -------------------------------
    # 2️⃣ FEES
    # -------------------------------
    elif any(fuzzy_match(w, ["fee", "fees", "payment", "amount"], 0.75) for w in words):
        fee = FeeModel.get_by_roll(roll)
        if not fee:
            return jsonify({"reply": "💰 No fee records found for you."})

        pending = fee.amount_due - fee.amount_paid
        return jsonify({
            "reply": (
                "💰 **Your Fee Status**\n"
                f"- Semester: {fee.semester}\n"
                f"- Total Due: ₹{fee.amount_due}\n"
                f"- Paid: ₹{fee.amount_paid}\n"
                f"- Pending: ₹{pending}\n"
                f"- Due Date: {fee.due_date}"
            )
        })

    # -------------------------------
    # 3️⃣ TIMETABLE
    # -------------------------------
    elif any(fuzzy_match(w, ["timetable", "schedule", "class", "lecture"], 0.75) for w in words):
        timetable = TimetableModel.get_all()
        if not timetable:
            return jsonify({"reply": "🗓 No timetable entries found."})

        reply = "🗓 **Your Timetable**\n"
        for t in timetable:
            reply += f"- {t.day}: {t.subject} ({t.start_time}-{t.end_time})\n"

        return jsonify({"reply": reply})

    # -------------------------------
    # 🔥 4️⃣ COLLEGE INFO (IMPORTANT)
    # -------------------------------
    elif any(key in msg for key in ["rule", "policy", "office", "library"]):
        for k, v in COLLEGE_INFO.items():
            if k in msg:
                return jsonify({"reply": f"🏫 {v}"})

        return jsonify({
            "reply": "🏫 You can ask about office timings, library rules, or attendance policy."
        })

    # -------------------------------
    # 5️⃣ ELIGIBILITY CHECK
    # -------------------------------
    elif any(word in msg for word in ["eligible", "eligibility"]):
        status, message = StudentModel.check_eligibility(roll)
        return jsonify({"reply": f"🎓 {message}"})

    # -------------------------------
    # 6️⃣ SMART ALERTS (CHAT + EMAIL)
    # -------------------------------
    elif "alert" in msg or "warning" in msg:
        alerts, email = StudentModel.get_alerts(roll)

        if not alerts:
            return jsonify({"reply": "✅ No alerts. Everything looks good!"})

        try:
            send_alert_email(email, alerts)
        except Exception as e:
            print("❌ Email alert failed:", e)

        reply = "🚨 **Important Alerts**\n"
        for a in alerts:
            reply += f"- {a}\n"

        reply += "\n📧 Alerts have also been sent to your email."

        return jsonify({"reply": reply})

    # -------------------------------
    # 7️⃣ AI FALLBACK (LAST ONLY)
    # -------------------------------
    chat_history.append(f"User: {user_msg}")
    chat_history = chat_history[-10:]
    session["chat_history"] = chat_history

    instruction = (
        "You are a helpful student assistant. "
        "Always give complete, well-structured answers. "
        "Keep explanations simple and clear."
    )

    contents = [instruction] + chat_history

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )
        bot_reply = response.text.strip() if response.text else \
            "🤖 I can help with attendance, fees, timetable, eligibility, or college rules."

    except Exception:
        bot_reply = ask_local_llm(user_msg)

    chat_history.append(f"Bot: {bot_reply}")
    session["chat_history"] = chat_history

    return jsonify({"reply": bot_reply})

# controllers/chat_controller.py
from flask import Blueprint, request, jsonify
from models.student_model import StudentModel
from models.fee_model import FeeModel
from models.timetable_model import TimetableModel
from utils.ai_client import client, MODEL

chat = Blueprint("chat", __name__)

# shared chat history (AI memory)
chat_history = []


# -------------------------------
# AI + DB BASED RESPONSE
# -------------------------------
@chat.route("/get_response", methods=["POST"])
def get_response():
    global chat_history

    data = request.get_json()
    user_msg = data.get("message", "")

    if not user_msg:
        return jsonify({"reply": "Please enter a message."})

    roll = ''.join(filter(str.isalnum, user_msg)).upper()
    roll_check = roll.startswith("R") and len(roll) >= 3

    # --------------------------------------------
    # If student roll detected → Fetch DB details
    # --------------------------------------------
    if roll_check:

        student = StudentModel.get_by_roll(roll)
        if not student:
            return jsonify({"reply": "No student found with that roll number."})

        fee = FeeModel.get_by_roll(roll)
        timetable = TimetableModel.get_all()

        reply = "📘 **Student Full Details**\n\n"
        reply += f"- Name: {student.name}\n"
        reply += f"- Roll: {student.roll}\n"
        reply += f"- Department: {student.department}\n"
        reply += f"- Year: {student.year}\n"
        reply += f"- Attendance: {student.attendance}%\n"
        reply += f"- Email: {student.email}\n\n"

        # Fee details
        if fee:
            pending = fee.amount_due - fee.amount_paid
            reply += "💰 **Fee Status:**\n"
            reply += f"- Semester: {fee.semester}\n"
            reply += f"- Due: ₹{fee.amount_due}\n"
            reply += f"- Paid: ₹{fee.amount_paid}\n"
            reply += f"- Pending: ₹{pending}\n"
            reply += f"- Due Date: {fee.due_date}\n\n"

        # Timetable
        reply += "🗓 **Timetable:**\n"
        for t in timetable:
            reply += (
                f"- {t.day}: {t.subject} "
                f"({t.start_time}-{t.end_time}) | {t.instructor} | {t.location}\n"
            )

        return jsonify({"reply": reply})

    # --------------------------------------------
    # If no roll → Use Gemini AI
    # --------------------------------------------
    chat_history.append(f"User: {user_msg}")

    # keep memory short
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]

    instruction = (
        "You are Student Assistant AI. "
        "Use clean formatting, bullet points, emojis, and keep responses helpful."
    )

    contents = [instruction] + chat_history

    response = client.models.generate_content(
        model=MODEL,
        contents=contents
    )

    bot_reply = response.text or "No response."

    chat_history.append(f"Bot: {bot_reply}")

    return jsonify({"reply": bot_reply})

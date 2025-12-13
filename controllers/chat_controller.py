# controllers/chat_controller.py
from flask import Blueprint, request, jsonify
from models.student_model import StudentModel
from models.fee_model import FeeModel
from models.timetable_model import TimetableModel
from utils.ai_client import client, MODEL
from utils.local_llm import ask_local_llm

chat = Blueprint("chat", __name__)

# shared chat history (global memory)
chat_history = []


@chat.route("/get_response", methods=["POST"])
def get_response():
    global chat_history

    data = request.get_json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Please enter a message."})

    # --------------------------------------------
    # DB MODE (roll number detected)
    # --------------------------------------------
    roll = ''.join(filter(str.isalnum, user_msg)).upper()
    if roll.startswith("R") and len(roll) >= 3:

        student = StudentModel.get_by_roll(roll)
        if not student:
            return jsonify({"reply": "No student found with that roll number."})

        fee = FeeModel.get_by_roll(roll)
        timetable = TimetableModel.get_all()

        reply = "📘 **Student Details**\n\n"
        reply += f"- Name: {student.name}\n"
        reply += f"- Roll: {student.roll}\n"
        reply += f"- Department: {student.department}\n"
        reply += f"- Year: {student.year}\n"
        reply += f"- Attendance: {student.attendance}%\n"
        reply += f"- Email: {student.email}\n\n"

        if fee:
            pending = fee.amount_due - fee.amount_paid
            reply += "💰 **Fee Status**\n"
            reply += f"- Semester: {fee.semester}\n"
            reply += f"- Due: ₹{fee.amount_due}\n"
            reply += f"- Paid: ₹{fee.amount_paid}\n"
            reply += f"- Pending: ₹{pending}\n"
            reply += f"- Due Date: {fee.due_date}\n\n"

        reply += "🗓 **Timetable**\n"
        for t in timetable:
            reply += f"- {t.day}: {t.subject} ({t.start_time}-{t.end_time}) | {t.instructor}\n"

        return jsonify({"reply": reply})

    # --------------------------------------------
    # AI MODE (Gemini → Local fallback)
    # --------------------------------------------
    chat_history.append(f"User: {user_msg}")
    chat_history = chat_history[-20:]  # hard cap

    # ---- Gemini prompt (rich) ----
    instruction = (
        "You are a helpful Student Assistant. "
        "Answer clearly, concisely, and politely. "
        "Use emojis only if helpful."
    )

    contents = [instruction] + chat_history

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )
        bot_reply = response.text.strip() if response.text else "No response."

    except Exception:
        recent_msgs = []

        for msg in chat_history[-4:]:
            if msg.startswith("User:"):
                recent_msgs.append(msg.replace("User:", "").strip())

        joined_prompt = "\n".join(recent_msgs[-2:])
        bot_reply = ask_local_llm(joined_prompt)

    chat_history.append(f"Bot: {bot_reply}")

    return jsonify({"reply": bot_reply})

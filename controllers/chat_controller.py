# controllers/chat_controller.py
from flask import Blueprint, request, jsonify, session
from models.student_model import StudentModel
from models.fee_model import FeeModel
from models.timetable_model import TimetableModel
from utils.ai_client import client, MODEL
from utils.local_llm import ask_local_llm
import difflib


chat = Blueprint("chat", __name__)



def fuzzy_match(word, keywords, threshold=0.75):
    """
    Returns True if 'word' closely matches any keyword.
    """
    for key in keywords:
        if difflib.SequenceMatcher(None, word, key).ratio() >= threshold:
            return True
    return False


@chat.route("/get_response", methods=["POST"])
def get_response():
    
    global chat_history
    chat_history = session.get("chat_history", [])

    data = request.get_json()
    user_msg = data.get("message", "").strip()

    roll = session.get("user_roll")

    if not roll:
        return jsonify({
        "reply": "🔒 Please login to access your academic information."
    })

    if "r0" in user_msg.lower():
        return jsonify({
        "reply": "🔒 For security reasons, I can only show your own data. Please ask without roll number."
    })


   # Attendance intent (handle spelling mistakes)
    words = user_msg.split()

# Attendance intent (fuzzy)
    if any(fuzzy_match(w, ["attendance", "attendence", "attend"], 0.75) for w in words):
        student = StudentModel.get_by_roll(roll)
        return jsonify({
        "reply": f"📊 Your attendance is {student.attendance}%."
    })


    elif any(fuzzy_match(w, ["fee", "fees", "payment", "amount"], 0.75) for w in words):
        fee = FeeModel.get_by_roll(roll)

        if not fee:
            return jsonify({
                "reply": "💰 No fee records found for you."
            })

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


    elif any(fuzzy_match(w, ["timetable", "schedule", "class", "lecture"], 0.75) for w in words):
        timetable = TimetableModel.get_all()

        if not timetable:
            return jsonify({
                "reply": "🗓 No timetable entries found."
            })

        reply = "🗓 **Your Timetable**\n"
        for t in timetable:
            reply += f"- {t.day}: {t.subject} ({t.start_time}-{t.end_time})\n"

        return jsonify({"reply": reply})

    # --------------------------------------------
    # AI MODE (Gemini → Local fallback)
    # --------------------------------------------

    chat_history.append(f"User: {user_msg}")
    chat_history = chat_history[-10:]   # keep last 10 only
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
            "🤖 I’m here to help! Please ask about attendance, fees, or timetable."

    except Exception:
        # Local LLM fallback
        bot_reply = ask_local_llm(user_msg)

    chat_history.append(f"Bot: {bot_reply}")
    session["chat_history"] = chat_history

    return jsonify({"reply": bot_reply})


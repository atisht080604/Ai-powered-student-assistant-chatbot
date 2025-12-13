from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# app.py
from flask import Flask
from config import SECRET_KEY, GOOGLE_API_KEY, MODEL_NAME
from google import genai
from utils.ai_client import client, MODEL



# Create Flask app FIRST
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_PERMANENT'] = False



# --- Initialize GenAI ---
from google import genai
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# --- Register DB ---
from utils.db import engine


# --- Register Controllers (BLUEPRINTS) ---
# ⭐ MUST come AFTER app = Flask(...)
from controllers.main_controller import main
from controllers.user_controller import user
from controllers.admin_controller import admin
from controllers.chat_controller import chat
from controllers.otp_controller import otp    
from controllers.profile_controller import profile

app.register_blueprint(main)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(chat)
app.register_blueprint(otp)
app.register_blueprint(profile)

# app.register_blueprint(otp)  # after making it


# No-cache for admin pages
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(debug=True)

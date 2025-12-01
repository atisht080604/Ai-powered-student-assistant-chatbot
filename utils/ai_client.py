# utils/ai_client.py

import os
from google import genai

# ---------------------------------------
# Load your API Key (read from .env or set manually)
# ---------------------------------------
# IF USING .env:
# Ensure in app.py you call: load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("Google API Key not found! Set GOOGLE_API_KEY in .env")

# Set env variable for client
os.environ["GOOGLE_API_KEY"] = API_KEY

# ---------------------------------------
# Initialize AI Client
# ---------------------------------------
client = genai.Client()
MODEL = "models/gemini-2.0-flash"

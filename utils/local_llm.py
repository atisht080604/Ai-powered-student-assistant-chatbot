import requests
import os

MODEL_NAME = os.getenv("LOCAL_LLM_MODEL", "mistral")

def ask_local_llm(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"""
You are a friendly student assistant.
Reply casually like a human.
Keep answers SHORT (2–4 lines max).
Do NOT explain what you are doing.

User: {prompt}
Assistant:
""",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 512,
            "num_predict": 120
        }
    }

    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json=payload,
            timeout=25
        )
        return r.json().get("response", "").strip()
    except Exception:
        return "⚠️ Local assistant is busy. Please try again."

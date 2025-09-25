import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
# load config
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.json"
load_dotenv()
with open(CONFIG_PATH) as f:
    CFG = json.load(f)

DEFAULT_MODEL = CFG.get("model", "gpt-5-nano")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_reply(user_text: str, override_model: str = None) -> str:
    """Send text to GPT and return the reply. Uses override_model if provided."""
    model = override_model or DEFAULT_MODEL
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise, helpful personal assistant. Keep replies short unless asked for detail."
                },
                {
                    "role": "user",
                    "content": user_text
                },
            ],
            temperature= 0.3,
            max_tokens=200,
        )
        text = resp.choices[0].message.content or ""
        return text.strip()
    except Exception as e:
        return f"⚠️ API error: {e}"

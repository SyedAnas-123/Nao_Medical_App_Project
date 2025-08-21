# (Flask backend: GPT translation only)

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# OpenAI (new SDK)
from openai import OpenAI

load_dotenv()
OPEN_AI_API_KEY =os.environ.get('OPEN_AI_API_KEY')
OPEN_AI_BASE_URL = os.environ.get('OPEN_AI_BASE_URL')

app = Flask(__name__)

# Init OpenAI client
client = OpenAI(
    api_key= OPEN_AI_API_KEY ,
    base_url= OPEN_AI_BASE_URL 
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/translate")
def translate():
    """
    Receives JSON: { text: str, from_lang: "en-US", to_lang: "ur-PK" }
    Uses GPT-4o-mini to translate with medical accuracy.
    Returns: { translated: str }
    """
    try:
        data = request.get_json(force=True)
        text = (data or {}).get("text", "").strip()
        from_lang = (data or {}).get("from_lang", "auto")
        to_lang = (data or {}).get("to_lang", "en-US")

        if not OPEN_AI_API_KEY:
            return jsonify({"error": "Missing OPENAI_API_KEY"}), 500
        if not text:
            return jsonify({"error": "Missing text"}), 400

        # Convert BCP-47 code to readable name hint for GPT
        # Simple mapping (extend if needed)
        code_to_name = {
            "en-US": "English",
            "en-GB": "English (UK)",
            "hi-IN": "Hindi",
            "es-ES": "Spanish",
            "es-MX": "Spanish (Mexico)",
            "de-DE": "German",
            "fr-FR": "French",
        
        }
        to_lang_name = code_to_name.get(to_lang, to_lang)
        from_lang_name = code_to_name.get(from_lang, "auto-detect")

        system_prompt = (
            "You are a professional medical interpreter. "
            f"Translate from {from_lang_name} to {to_lang_name}. "
            "Preserve patient intent and medical terminology. "
            "Do not add explanations. Output only the translation."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        translated = (resp.choices[0].message.content or "").strip()
        return jsonify({"translated": translated})

    except Exception as e:
        print("Translate error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Flask dev server
    app.run(host="127.0.0.1", port=5000, debug=True)

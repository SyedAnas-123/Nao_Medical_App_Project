# (Flask backend: GPT translation only)
# Import standard libraries
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Import OpenAI's official SDK
from openai import OpenAI

# Load environment variables from .env file (API keys, base URL, etc.)
load_dotenv()
OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')   # Your OpenAI API key
OPEN_AI_BASE_URL = os.environ.get('OPEN_AI_BASE_URL') # Optional: custom base URL

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client with API key + base URL
client = OpenAI(
    api_key=OPEN_AI_API_KEY,
    base_url=OPEN_AI_BASE_URL
)

# Home route – renders index.html (the frontend)
@app.route("/")
def index():
    return render_template("index.html")

# Translation API endpoint
@app.post("/api/translate")
def translate():
    """
    Receives JSON body:
      { "text": str, "from_lang": "en-US", "to_lang": "ur-PK" }
    
    Uses GPT-4o-mini model for medical translation.
    Returns JSON:
      { "translated": str }
    """
    try:
        # Parse JSON from request
        data = request.get_json(force=True)
        text = (data or {}).get("text", "").strip()
        from_lang = (data or {}).get("from_lang", "auto")
        to_lang = (data or {}).get("to_lang", "en-US")

        # Check for missing API key or text
        if not OPEN_AI_API_KEY:
            return jsonify({"error": "Missing OPENAI_API_KEY"}), 500
        if not text:
            return jsonify({"error": "Missing text"}), 400

        # Mapping of language codes → human-readable names
        code_to_name = {
            "en-US": "English",
            "en-GB": "English (UK)",
            "hi-IN": "Hindi",
            "es-ES": "Spanish",
            "es-MX": "Spanish (Mexico)",
            "de-DE": "German",
            "fr-FR": "French",
        }

        # Convert codes to names for GPT prompt
        to_lang_name = code_to_name.get(to_lang, to_lang)
        from_lang_name = code_to_name.get(from_lang, "auto-detect")

        # System prompt for GPT (ensures accuracy & medical context)
        system_prompt = (
            "You are a professional medical interpreter. "
            f"Translate from {from_lang_name} to {to_lang_name}. "
            "Preserve patient intent and medical terminology. "
            "Do not add explanations. Output only the translation."
        )

        # Call OpenAI GPT model
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,  # low temperature → more accurate
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        # Extract translated text
        translated = (resp.choices[0].message.content or "").strip()
        return jsonify({"translated": translated})

    except Exception as e:
        # Catch & log any errors
        print("Translate error:", e)
        return jsonify({"error": str(e)}), 500

# Run Flask in development mode
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

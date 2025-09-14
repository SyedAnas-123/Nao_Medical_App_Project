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





#*  ****************************************************************************************************************

# 🚀 Flask Code Breakdown (Teaching Style)
# 1. Setup & Initialization
# import os
# from flask import Flask, render_template, request, jsonify
# from dotenv import load_dotenv
# from openai import OpenAI


# os → environment variables handle karne ke liye.

# Flask → web server banata hai.

# render_template → HTML pages load karne ke liye (frontend).

# request → client (browser/frontend) se data receive karne ke liye.

# jsonify → Python dict → JSON response.

# dotenv → .env file se secret values (API key, URL) load karta hai.

# OpenAI → OpenAI ka SDK jo API ko call karta hai.

# 2. Environment Variables
# load_dotenv()
# OPEN_AI_API_KEY = os.environ.get('OPEN_AI_API_KEY')
# OPEN_AI_BASE_URL = os.environ.get('OPEN_AI_BASE_URL')


# .env file ke andar sensitive info store hoti hai (API keys).

# OPEN_AI_API_KEY → aapki GPT API key.

# OPEN_AI_BASE_URL → agar aap custom endpoint use karte ho (warna default OpenAI ka URL hi use hoga).

# 3. Flask App & OpenAI Client
# app = Flask(__name__)

# client = OpenAI(
#     api_key=OPEN_AI_API_KEY,
#     base_url=OPEN_AI_BASE_URL
# )


# app = Flask(__name__) → Flask application create ho gayi.

# client = OpenAI(...) → GPT model ko call karne ka client ban gaya.

# 4. Home Route
# @app.route("/")
# def index():
#     return render_template("index.html")


# Jab koi browser me http://127.0.0.1:5000/ open karega → index.html file show hogi.

# Ye frontend (UI) hai jahan user text enter karega.

# 5. Translation API
# @app.post("/api/translate")
# def translate():
#     ...


# Ye API endpoint hai. Matlab jab frontend POST request bhejega /api/translate pe, to ye function chalega.

# Step by Step Inside Function:
# (a) Request Parse karna
# data = request.get_json(force=True)
# text = (data or {}).get("text", "").strip()
# from_lang = (data or {}).get("from_lang", "auto")
# to_lang = (data or {}).get("to_lang", "en-US")


# Frontend se JSON receive hota hai, example:

# { "text": "Hello", "from_lang": "en-US", "to_lang": "ur-PK" }


# Extract karte ho:

# text → jo user ne likha hai.

# from_lang → source language (auto detect if missing).

# to_lang → target language (default: English).

# (b) Validation
# if not OPEN_AI_API_KEY:
#     return jsonify({"error": "Missing OPENAI_API_KEY"}), 500
# if not text:
#     return jsonify({"error": "Missing text"}), 400


# Agar API key missing hai → error 500.

# Agar text empty hai → error 400.

# (c) Language Code → Human Readable
# code_to_name = {
#     "en-US": "English",
#     "en-GB": "English (UK)",
#     "hi-IN": "Hindi",
#     "es-ES": "Spanish",
#     "es-MX": "Spanish (Mexico)",
#     "de-DE": "German",
#     "fr-FR": "French",
# }


# Ye dictionary codes ko readable naam me convert karta hai.
# Example: ur-PK → Urdu (agar added ho).

# (d) GPT Prompt
# system_prompt = (
#     "You are a professional medical interpreter. "
#     f"Translate from {from_lang_name} to {to_lang_name}. "
#     "Preserve patient intent and medical terminology. "
#     "Do not add explanations. Output only the translation."
# )


# Ye GPT ko instruction deta hai ke sirf translation output kare, explanation nahi.

# Context: Medical translation.

# (e) GPT API Call
# resp = client.chat.completions.create(
#     model="gpt-4o-mini",
#     temperature=0.2,
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": text},
#     ],
# )


# model="gpt-4o-mini" → fast + accurate translation ke liye.

# temperature=0.2 → output stable aur less random.

# Messages → GPT ko conversation context dete hain.

# (f) Extract GPT Response
# translated = (resp.choices[0].message.content or "").strip()
# return jsonify({"translated": translated})


# GPT ka output extract hota hai.

# Example: { "translated": "ہیلو" }

# (g) Error Handling
# except Exception as e:
#     print("Translate error:", e)
#     return jsonify({"error": str(e)}), 500


# Agar kuch bhi crash ho gaya to server user ko error message bhej dega.

# 6. Run Server
# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)


# Flask app run hoti hai local server pe (localhost:5000).

# debug=True → errors console me clearly show hote hain.

# 🎯 Simple Summary (as if you’re a student):

# Flask app banaya.

# index.html serve hota hai as frontend.

# User text bhejta hai /api/translate pe.

# Backend GPT ko call karta hai → translation return karta hai.
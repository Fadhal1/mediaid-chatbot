# File: /api/chat.py
import os
import cohere
import json
from flask import Flask, request, jsonify

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

# --- Function to load your local medical data ---
def load_local_data():
    try:
        with open('mediaid_full_dataset.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading local data: {e}")
        return {}

# Load the data once when the server starts
local_data = load_local_data()

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Setup ---
        api_key = os.environ.get("GEMINI_API_KEY") 
        co = cohere.Client(api_key)
        request_data = request.get_json()
        user_prompt = request_data.get('prompt', '').lower()

        # --- 2. Search local data for keywords ---
        context_data = None
        for key in local_data:
            if key in user_prompt:
                context_data = local_data[key]
                break
        
        # --- 3. If a local match is found, force the AI into the template ---
        if context_data:
            # The AI's unbreakable persona and rules for this specific task
            preamble = (
                "You are a data formatting AI. Your only function is to populate an HTML template with provided medical context. "
                "Your tone must be clinical and direct, using only the provided data. "
                "You MUST NOT use newline characters (`\n`). You MUST use `<br>` for line breaks. "
                "Your entire response MUST be a single block of HTML starting with '<b>Cause:'."
            )

            # The direct command given to the AI, with the template repeated for emphasis
            message_for_ai = (
                f"Using the provided context, populate the following HTML template. "
                f"Do not add any text before or after the template. "
                f"CONTEXT: {json.dumps(context_data)}\n\n"
                f"TEMPLATE TO POPULATE:\n"
                "<b>Cause:</b> [Insert clinical summary of cause]\n"
                "<b>Signs & Symptoms:</b> [Insert clinical list of symptoms]\n"
                "<b>Drugs:</b> [Insert clinical list of drugs]\n"
                "<b>Prevention:</b> [Insert clinical summary of prevention]\n"
                "<b>Advice:</b> [Insert clinical summary of advice]"
            )

            response = co.chat(
                message=message_for_ai,
                model="command-r",
                preamble=preamble
            )
            
            # Final check: sometimes the AI still adds extra newlines. We remove them.
            clean_reply = response.text.replace('\n', ' ')
            return jsonify({"reply": clean_reply})

        # --- 4. If NO local match, handle as a general query ---
        else:
            fallback_preamble = (
                "You are MediAid, a professional medical aid. If a user asks a question you cannot answer with specific data, "
                "you must state that you can only provide information on specific conditions and that for personal medical advice, "
                "they must consult a healthcare professional. Do not attempt to answer questions outside of your scope."
            )
            
            response = co.chat(
                message=user_prompt,
                model="command-r",
                preamble=fallback_preamble
            )
            
            return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

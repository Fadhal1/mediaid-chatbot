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
                "You are an information-structuring AI. You will receive context about a medical condition. "
                "Your task is to populate a predefined HTML template with this information. "
                "Your tone must be clinical and direct. "
                "You MUST NOT add any extra text, introductions, or conclusions. "
                "Your entire response MUST start with '<b>Cause:' and end with the final piece of advice."
            )

            # The direct command given to the AI
            message_for_ai = (
                f"Use the following context to populate the template:\n"
                f"CONTEXT: {json.dumps(context_data)}\n\n"
                f"TEMPLATE:\n"
                "<b>Cause:</b> [Insert a clinical summary of the cause here]\n"
                "<b>Signs & Symptoms:</b> [Insert a clinical list of symptoms here]\n"
                "<b>Drugs:</b> [Insert a clinical list of drugs here]\n"
                "<b>Prevention:</b> [Insert a clinical summary of prevention methods here]\n"
                "<b>Advice:</b> [Insert a clinical summary of the advice here]"
            )

            response = co.chat(
                message=message_for_ai,
                model="command-r",
                preamble=preamble
            )
            
            # We now return the AI's response, which should be perfectly formatted.
            return jsonify({"reply": response.text})

        # --- 4. If NO local match, handle as a general query ---
        else:
            fallback_preamble = (
                "You are MediAid, a professional pharmacist AI. Your primary role is to provide information on specific medical conditions based on your internal data. "
                "If a user asks a question you cannot answer with specific data, you must state that you can only provide information on specific conditions and that for personal medical advice, they must consult a healthcare professional. "
                "Do not attempt to answer questions outside of your scope."
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

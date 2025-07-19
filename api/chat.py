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
        # --- 1. Get user's prompt ---
        request_data = request.get_json()
        user_prompt = request_data.get('prompt', '').lower()
        if not user_prompt:
            return jsonify({"error": "Prompt is required."}), 400

        # --- 2. Search local data for an exact match ---
        context_data = None
        for key in local_data:
            if key in user_prompt:
                context_data = local_data[key]
                break

        # --- 3. THE CORRECT LOGIC: If we find a local match, build the reply directly! ---
        if context_data:
            print(f"Found local data for '{user_prompt}'. Replying WITHOUT AI.")
            
            # Manually build the perfect, styled HTML response from your dataset
            # using the Tailwind classes from your working example.
            heading_class = "font-bold text-green-900"
            
            reply_html = (
                f"<span class='{heading_class}'>Cause:</span> {context_data.get('cause', 'N/A')}<br>"
                f"<span class='{heading_class}'>Signs & Symptoms:</span> {', '.join(context_data.get('signs_and_symptoms', []))}<br>"
                f"<span class='{heading_class}'>Drugs:</span> {', '.join(context_data.get('drugs', []))}<br>"
                f"<span class='{heading_class}'>Prevention:</span> {context_data.get('prevention', 'N/A')}<br>"
                f"<span class='{heading_class}'>Advice:</span> {context_data.get('advice', 'N/A')}"
            )
            
            # Return the locally-built HTML and STOP.
            return jsonify({"reply": reply_html})
        
        # --- 4. If NO local match was found, THEN and ONLY THEN, call the AI ---
        else:
            print(f"No local data for '{user_prompt}'. Calling Cohere AI for fallback.")
            
            api_key = os.environ.get("GEMINI_API_KEY") 
            co = cohere.Client(api_key)
            
            fallback_preamble = (
                "You are MediAid, a friendly AI health companion. A user has asked a question. Respond in a brief, helpful, and conversational tone. "
                "Always recommend that the user consults a healthcare professional for personal medical advice."
            )
            
            response = co.chat(message=user_prompt, model="command-r", preamble=fallback_preamble)
            return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

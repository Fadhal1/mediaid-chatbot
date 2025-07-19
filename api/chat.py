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
        found_key = ""
        for key in local_data:
            if key in user_prompt:
                context_data = local_data[key]
                found_key = key
                break
        
        # --- 3. Define the AI's personality and the message it will receive ---
        preamble = "You are MediAid, a friendly health companion. You provide clear, structured health information. Always conclude your response by strongly recommending that the user consult a healthcare professional for personal medical advice."
        message_for_ai = user_prompt # By default, use the user's original message

        # --- 4. THE SMART PART: If we found a match, transform the prompt ---
        if context_data:
            # Rephrase the user's message into a command for information
            message_for_ai = f"Give me a detailed and structured overview of {found_key}. Include what it is, common treatments, and prevention advice."
            
            # We can even add the context to the preamble for this specific call
            context_str = (
                f"Use the following information to inform your answer about '{found_key}':\n"
                f"- Signs and Symptoms: {', '.join(context_data.get('signs_and_symptoms', []))}\n"
                f"- Recommended Drugs: {', '.join(context_data.get('drugs', []))}"
            )
            preamble = f"{preamble}\n\nHere is some context to help you:\n{context_str}"


        # --- 5. Call Cohere with the (potentially new) message and preamble ---
        response = co.chat(
            message=message_for_ai,
            model="command-r",  # Let's upgrade to a more powerful model for better results
            preamble=preamble
        )

        # --- 6. Send the detailed response back ---
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

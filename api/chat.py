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
        
        # --- 3. Define the AI's instructions and message ---
        preamble = (
            "You are MediAid, a helpful health assistant. You will be given a user's question and some context. "
            "Your task is to answer the user's question conversationally while structuring the key information in HTML. "
            "You MUST format the structured part of your response using the exact HTML template provided. "
            "Conclude by advising the user to consult a healthcare professional."
        )
        message_for_ai = user_prompt

        # --- 4. THE KEY CHANGE: If we find a match, create an example for the AI ---
        if context_data:
            # This is the exact HTML template we want the AI to follow.
            example_format = (
                "<b>Cause:</b> [AI-generated summary of the cause here]<br>"
                "<b>Signs & Symptoms:</b> [AI-generated list of symptoms here]<br>"
                "<b>Drugs:</b> [AI-generated list of drugs here]<br>"
                "<b>Prevention:</b> [AI-generated summary of prevention here]<br>"
                "<b>Advice:</b> [AI-generated summary of advice here]"
            )
            
            # Combine the context and the example format into a single, powerful prompt for the AI.
            message_for_ai = (
                f"The user is asking about '{found_key}'. Here is the information I have:\n"
                f"CONTEXT: {json.dumps(context_data)}\n\n"
                f"Based on the context, please answer the user's question. Start with a brief, friendly introductory sentence. "
                f"Then, you MUST present the detailed information using this exact HTML format:\n"
                f"EXAMPLE FORMAT:\n{example_format}"
            )

        # --- 5. Call Cohere with our highly specific instructions ---
        response = co.chat(
            message=message_for_ai,
            model="command-r",  # A powerful model that can follow complex instructions
            preamble=preamble
        )

        # --- 6. Send the AI's structured response back ---
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

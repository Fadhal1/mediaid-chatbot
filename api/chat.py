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
        # On Vercel, the file path is relative to the root
        with open('mediaid_full_dataset.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: mediaid_full_dataset.json not found.")
        return {}
    except json.JSONDecodeError:
        print("ERROR: Could not decode mediaid_full_dataset.json.")
        return {}

# Load the data once when the server starts
local_data = load_local_data()

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Get Cohere API Key ---
        api_key = os.environ.get("GEMINI_API_KEY") 
        if not api_key:
            print("ERROR: Cohere API Key not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        co = cohere.Client(api_key)

        # --- 2. Get Prompt from Frontend ---
        request_data = request.get_json()
        user_prompt = request_data.get('prompt', '').lower()
        if not user_prompt:
            return jsonify({"error": "Prompt is required."}), 400

        # --- 3. THIS IS THE NEW LOGIC: Search local data first ---
        context_data = None
        for key in local_data:
            if key in user_prompt:
                context_data = local_data[key]
                break

        preamble = "You are MediAid, a friendly and professional health companion. Your primary goal is to provide clear, helpful health information. If you have specific context, base your answer primarily on that. Always advise users to consult a healthcare professional for personal medical advice."
        
        # If we found data, build a rich context for the AI
        if context_data:
            context_str = (
                f"Use the following information to answer the user's question about '{context_data.get('name', '')}':\n"
                f"- Cause: {context_data.get('cause', 'N/A')}\n"
                f"- Signs and Symptoms: {', '.join(context_data.get('signs_and_symptoms', []))}\n"
                f"- Recommended Drugs: {', '.join(context_data.get('drugs', []))}\n"
                f"- Prevention Methods: {context_data.get('prevention', 'N/A')}\n"
                f"- General Advice: {context_data.get('advice', 'N/A')}"
            )
            # Add the specific context to the general preamble
            preamble = f"{preamble}\n\nStrictly use the following context for your answer:\n{context_str}"

        # --- 4. Call Cohere Chat API with the new, smarter preamble ---
        response = co.chat(
            message=user_prompt,
            model="command-light",
            preamble=preamble # This gives the AI its instructions and context
        )

        # --- 5. Send the AI's response back ---
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

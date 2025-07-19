# File: /api/chat.py
import os
import cohere
from flask import Flask, request, jsonify

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Get Cohere API Key ---
        # We are reusing the same environment variable name for simplicity
        api_key = os.environ.get("GEMINI_API_KEY") 
        if not api_key:
            print("ERROR: Cohere API Key not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        # --- 2. Initialize the Cohere Client ---
        co = cohere.Client(api_key)

        # --- 3. Get Prompt from Frontend ---
        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        user_prompt = request_data['prompt']

        # --- 4. Call the Cohere Chat API ---
        response = co.chat(
            message=user_prompt,
            model="command-light"  # Using a fast and reliable model for the trial tier
        )

        # --- 5. Send the AI's text response back to the frontend ---
        return jsonify({"reply": response.text})

    except Exception as e:
        # This will log any errors from Cohere or our code
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

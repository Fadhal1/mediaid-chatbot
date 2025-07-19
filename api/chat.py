# File: /api/chat.py
import os
import requests
from flask import Flask, request, jsonify

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

# THIS IS THE ONLY CHANGE: A smaller, more reliable model
MODEL_NAME = "microsoft/DialoGPT-medium"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Get API Key (your Hugging Face Token) ---
        hf_token = os.environ.get("GEMINI_API_KEY") 
        if not hf_token:
            print("ERROR: Hugging Face Token not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        # --- 2. Prepare the manual API request ---
        headers = {"Authorization": f"Bearer {hf_token}"}

        # --- 3. Get Prompt from Frontend ---
        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        user_prompt = request_data['prompt']

        # --- 4. Construct the payload for a "conversational" task ---
        payload = {
            "inputs": {
                "text": user_prompt
            }
        }

        # --- 5. Make the direct API call using 'requests' library ---
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() 
        response_data = response.json()

        # --- 6. Send Response Back ---
        generated_reply = response_data.get('generated_text', 'Sorry, I received a response but could not process it.')
        return jsonify({"reply": generated_reply})

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {http_err.response.content}")
        return jsonify({"error": f"Error from AI service: {http_err.response.status_code}"}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

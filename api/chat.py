# File: /api/chat.py
import os
import requests
from flask import Flask, request, jsonify

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

# FINAL ATTEMPT: Using the most basic, guaranteed-to-be-available model.
MODEL_NAME = "gpt2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        hf_token = os.environ.get("GEMINI_API_KEY") 
        if not hf_token:
            print("ERROR: Hugging Face Token not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        headers = {"Authorization": f"Bearer {hf_token}"}

        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        user_prompt = request_data['prompt']

        # The simplest possible payload for a text-generation task.
        payload = {
            "inputs": user_prompt
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() 
        response_data = response.json()

        # The response format for text-generation is a list containing a dictionary.
        generated_reply = response_data[0].get('generated_text', 'Sorry, I could not process that.')
        return jsonify({"reply": generated_reply})

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {http_err.response.content}")
        return jsonify({"error": f"Error from AI service: {http_err.response.status_code}"}), 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

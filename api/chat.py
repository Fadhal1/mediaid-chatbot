# File: /api/chat.py
import os
from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

# We will use a powerful open-source chat model from Mistral AI
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Get API Key (your Hugging Face Token) ---
        # We are still using the same environment variable name for simplicity
        api_key = os.environ.get("GEMINI_API_KEY") 
        if not api_key:
            print("ERROR: Hugging Face Token (HF_TOKEN/GEMINI_API_KEY) not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        # --- 2. Initialize the client ---
        client = InferenceClient(model=MODEL_NAME, token=api_key)

        # --- 3. Get Prompt from Frontend ---
        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        prompt = request_data['prompt']

        # --- 4. Call Hugging Face API ---
        # The 'text_generation' endpoint is used for this kind of model
        response = client.text_generation(prompt, max_new_tokens=250)

        # --- 5. Send Response Back ---
        # The response format is different from Gemini's
        return jsonify({"reply": response})

    except Exception as e:
        # This will log the specific error to your Vercel logs
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

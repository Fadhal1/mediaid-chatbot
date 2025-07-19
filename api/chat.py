# File: /api/chat.py
import os
from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

# We will use the same powerful open-source chat model
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Get API Key (your Hugging Face Token) ---
        api_key = os.environ.get("GEMINI_API_KEY") 
        if not api_key:
            print("ERROR: Hugging Face Token not found.")
            return jsonify({"error": "AI service is not configured."}), 500

        # --- 2. Initialize the client ---
        client = InferenceClient(model=MODEL_NAME, token=api_key)

        # --- 3. Get Prompt from Frontend ---
        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        user_prompt = request_data['prompt']

        # --- 4. Format the prompt for the Mistral model ---
        # This is the crucial fix. We wrap the prompt in instruction tags.
        formatted_prompt = f"[INST] {user_prompt} [/INST]"

        # --- 5. Call Hugging Face API with the correct method ---
        # We are back to using .text_generation, which exists.
        response = client.text_generation(formatted_prompt, max_new_tokens=250)

        # --- 6. Send Response Back ---
        return jsonify({"reply": response})

    except Exception as e:
        # This will log the specific error to your Vercel logs
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# File: /api/chat.py
# File: /api/chat.py
import os
import google.generativeai as genai
from flask import Flask, request, jsonify

# Vercel will automatically discover this 'app' object.
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    try:
        # --- 1. Configure API Key ---
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # This error will show up in your Vercel logs
            print("ERROR: GEMINI_API_KEY environment variable not found.")
            return jsonify({"error": "AI service is not configured."}), 500
        
        genai.configure(api_key=api_key)

        # --- 2. Get Prompt from Frontend ---
        request_data = request.get_json()
        if not request_data or 'prompt' not in request_data:
            return jsonify({"error": "Prompt is required."}), 400
        
        prompt = request_data['prompt']

        # --- 3. Call Gemini API ---
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)

        # --- 4. Send Response Back ---
        return jsonify({"reply": response.text})

    except Exception as e:
        # This will log the specific error to your Vercel logs for debugging
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# This part is not strictly needed for Vercel but is good practice
if __name__ == "__main__":
    app.run(debug=True)

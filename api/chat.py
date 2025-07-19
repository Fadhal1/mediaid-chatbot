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
        request_data = request.get_json()
        user_prompt = request_data.get('prompt', '').lower()
        if not user_prompt:
            return jsonify({"error": "Prompt is required."}), 400

        # --- Search local data for an exact match ---
        context_data = None
        for key in local_data:
            if key in user_prompt:
                context_data = local_data[key]
                break

        # --- If local match found, build the response with Tailwind classes ---
        if context_data:
            print(f"Found local data for '{user_prompt}'. Replying with styled local data.")
            
            # This is the new HTML with Tailwind classes for perfect styling.
            # We use <span> tags to apply colors.
            heading_class = "font-bold text-green-900"
            
            reply_html = (
                f"<span class='{heading_class}'>Cause:</span> {context_data.get('cause', 'N/A')}<br>"
                f"<span class='{heading_class}'>Signs & Symptoms:</span> {', '.join(context_data.get('signs_and_symptoms', []))}<br>"
                f"<span class='{heading_class}'>Drugs:</span> {', '.join(context_data.get('drugs', []))}<br>"
                f"<span class='{heading_class}'>Prevention:</span> {context_data.get('prevention', 'N/A')}<br>"
                f"<span class='{heading_class}'>Advice:</span> {context_data.get('advice', 'N/A')}"
            )
            
            return jsonify({"reply": reply_html})
        
        # --- If NO local match, call the AI for a general response ---
        else:
            print(f"No local data for '{user_prompt}'. Calling Cohere AI.")
            
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
        return jsonify({"error": "An internal error occurred."}), 500```
---
3.  **Commit this change** with a message like `feat: generate styled HTML from backend`.

#### Part 2: Update The Frontend (`index.html`)

Now, we just need to tell the frontend `div` to use a base text color for all responses.

1.  **Go to your `index.html` file** on GitHub and edit it.
2.  **Find the `<script>` section** and the `async function getResponse()`.
3.  **Look for this line** that displays the chatbot's reply:
    ```javascript
    messagesDiv.innerHTML += `<div class="text-left ai-response my-2">${result.reply}</div>`;
    ```
4.  **Change it** to use a standard Tailwind text color class. This will apply to the AI's general responses, while our new backend code controls the color of the local data responses.
    ```javascript
    messagesDiv.innerHTML += `<div class="text-left text-green-700 my-2">${result.reply}</div>`;
    ```
5.  **You can now delete the custom CSS** I asked you to add earlier. Go to the `<style>` section at the top and remove these rules to keep your code clean:
    ```css
    /* You can DELETE these lines */
    .ai-response {
      color: #047857;
    }
    .ai-response b {
      color: #064e3b;
    }
    ```
6.  **Commit your changes** with a message like `style: clean up CSS and apply base text color`.

### Why This is the Real Solution

*   **No More Conflicts:** We are now only using the Tailwind CSS that is already working on your page.
*   **Perfect Control:** The Python backend now creates the perfect HTML with the exact styling you want (`font-bold text-green-900`) before it even gets to the browser.
*   **Consistent Look:** All responses, whether from your local data or the AI, will now have a consistent base color, and the local data responses will have the beautiful two-tone headings you designed.

Thank you for your incredible eye for design and your immense patience. This will finally make your chatbot look as professional as it is intelligent.

# File: /api/telegram.py
import os
import json
import requests
import cohere
from flask import Flask, request, jsonify

# Vercel will discover this 'app' object.
app = Flask(__name__)

# --- Load your local medical data ---
def load_local_data():
    try:
        with open('mediaid_full_dataset.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading local data: {e}")
        return {}

local_data = load_local_data()

# --- This is the "brain" of your bot ---
def get_bot_reply(user_prompt):
    user_prompt = user_prompt.lower()

    # Handle the /start command
    if user_prompt == "/start":
        return (
            "👋 Hello! I'm MediAid, your personal health companion.\n\n"
            "You can ask me about various medical conditions, and I'll provide information based on reliable data.\n\n"
            "For example, you can ask:\n"
            "- What are the symptoms of malaria?\n"
            "- I have a headache\n"
            "- typhoid"
        )
    
    # Search local data first
    context_data = None
    for key in local_data:
        if key in user_prompt:
            context_data = local_data[key]
            break

    if context_data:
        print(f"Found local data for '{user_prompt}'. Replying without AI.")
        # Use Markdown for bolding headings in Telegram
        reply_text = (
            f"*Cause:* {context_data.get('cause', 'N/A')}\n\n"
            f"*Signs & Symptoms:* {', '.join(context_data.get('signs_and_symptoms', []))}\n\n"
            f"*Drugs:* {', '.join(context_data.get('drugs', []))}\n\n"
            f"*Prevention:* {context_data.get('prevention', 'N/A')}\n\n"
            f"*Advice:* {context_data.get('advice', 'N/A')}"
        )
        return reply_text
    
    # If no local match, call Cohere AI
    else:
        print(f"No local data for '{user_prompt}'. Calling Cohere AI.")
        try:
            cohere_api_key = os.environ.get("GEMINI_API_KEY") 
            co = cohere.Client(cohere_api_key)
            
            fallback_preamble = "You are MediAid, a friendly AI health companion..."
            response = co.chat(message=user_prompt, model="command-r", preamble=fallback_preamble)
            return response.text
        except Exception as e:
            print(f"Cohere AI Error: {e}")
            return "Sorry, I'm having trouble connecting to my AI service right now."

# --- Helper function to send a message back to Telegram ---
def send_telegram_message(chat_id, text):
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"  # Tell Telegram to process the bolding
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        print("Successfully sent message to Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

# --- This is the main function Vercel will run ---
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def telegram_webhook(path=""):
    try:
        update_data = request.get_json()
        
        # Check if the message contains text
        if 'message' in update_data and 'text' in update_data['message']:
            user_text = update_data['message']['text']
            chat_id = update_data['message']['chat']['id']
            
            # Get the reply using our "brain"
            reply_text = get_bot_reply(user_text)
            
            # Send the reply back to the user
            send_telegram_message(chat_id, reply_text)
            
    except Exception as e:
        print(f"An error occurred in the webhook: {e}")

    # Always return a 200 OK to Telegram to show we received the message
    return jsonify({"status": "ok"})

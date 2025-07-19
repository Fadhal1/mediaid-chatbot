# File: /api/telegram.py
import os
import json
import asyncio
import cohere
from flask import Flask, request, jsonify

# pip install python-telegram-bot
from telegram import Bot, Update
from telegram.ext import CallbackContext, Application

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

# This is where the function starts
def get_bot_reply(user_prompt):
    user_prompt = user_prompt.lower()

    # --- THIS IS THE NEW CODE ---
    if user_prompt == "/start":
        return (
            "👋 Hello! I'm MediAid, your personal health companion.\n\n"
            "You can ask me about various medical conditions, and I'll provide information based on reliable data.\n\n"
            "For example, you can ask:\n"
            "- What are the symptoms of malaria?\n"
            "- I have a headache\n"
            "- typhoid"
        )
    # --- END OF NEW CODE ---

    # 1. Search local data first
    context_data = None
    # ...the rest of the function stays the same...
    
    # 1. Search local data first
    context_data = None
    for key in local_data:
        if key in user_prompt:
            context_data = local_data[key]
            break

    if context_data:
        print(f"Found local data for '{user_prompt}'. Replying without AI.")
        reply_text = (
            f"Cause: {context_data.get('cause', 'N/A')}\n"
            f"Signs & Symptoms: {', '.join(context_data.get('signs_and_symptoms', []))}\n"
            f"Drugs: {', '.join(context_data.get('drugs', []))}\n"
            f"Prevention: {context_data.get('prevention', 'N/A')}\n"
            f"Advice: {context_data.get('advice', 'N/A')}"
        )
        return reply_text
    
    # 2. If no local match, call Cohere AI
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

# --- This is the function Vercel will run ---
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def telegram_webhook(path=""):
    # This is the main async function that processes a message
    async def process_update():
        telegram_token = os.environ.get("TELEGRAM_TOKEN")
        bot = Bot(token=telegram_token)
        
        update_data = request.get_json()
        update = Update.de_json(update_data, bot)
        
        if update.message and update.message.text:
            user_text = update.message.text
            chat_id = update.message.chat_id
            
            # Get the reply using our "brain"
            reply = get_bot_reply(user_text)
            
            # Send the reply back to the user on Telegram
            await bot.send_message(chat_id=chat_id, text=reply)

    # Run the async function from a sync Flask route
    asyncio.run(process_update())
    
    return jsonify({"status": "ok"})
```---
5.  **Commit this new file** with a message like `feat: add telegram webhook handler`. Vercel will automatically deploy it. Wait for the deployment to finish before the next stage.

---

### **Stage 4: Tell Telegram Where to Send Messages**

This is the final step. You will activate your bot by visiting a special URL in your browser.

1.  **Construct the URL.** You need to copy this URL structure and replace the two placeholders:
    `https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook?url=https://mediaid-chatbot.vercel.app/api/telegram`

2.  **Replace the placeholders:**
    *   Replace `<YOUR_TELEGRAM_TOKEN>` with the token you got from BotFather.
    *   Make sure the `url=` part correctly points to your live Vercel app URL, followed by `/api/telegram`.

3.  **Visit the URL.** Paste your final, completed URL into your phone's web browser and press Go.

4.  **Check the Response.** The browser will show a small piece of text. If it's successful, it will say:
    `{"ok":true,"result":true,"description":"Webhook was set"}`

**That's it!** Your Telegram bot is now live. Open Telegram, find the bot by its username, and send it a message like "malaria" or "hi". It should reply instantly. Congratulations

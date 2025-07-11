
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


GEMINI_API_KEY = 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@app.post("/api/ai")
async def ai_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    context = f"""
    You are MediAid – Local Drug Finder & Health Advice Chatbot.

    Instructions:
    - Chat interface where users can:
    - Ask about symptoms (e.g., "What can I use for headache?")
    - Ask about a drug (e.g., "What is Paracetamol used for?")
    - Ask general health questions (e.g., "When should I see a doctor for malaria?")
    - Give response in cordial but professional tone,
    - Do not go off-topic or discuss unrelated topics.
    - Stay motivational and supportive in your tone.

    Now here's a patient question:
    \"{prompt}\"
    """

    try:
        response = model.generate_content(context)
        print("Gemini API raw response:", response)
        # The google-generativeai SDK returns a response object with a 'text' attribute
        return {"text": getattr(response, 'text', str(response))}
    except Exception as e:
        print("Gemini API error:", e)
        return {"error": str(e)}

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from pydantic import BaseModel

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with your actual Gemini API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Add your API key here

# Initialize Gemini
try:
    genai.configure(api_key=AlzaSyBtx5RsZGgCScMyMEtGFb8gYABnT1xFgRc)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")  # Using latest model
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    model = None

class PromptRequest(BaseModel):
    prompt: str

@app.post("/api/ai")
async def ai_endpoint(request: PromptRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    context = f"""
    You are MediAid – a Local Drug Finder & Health Advice Chatbot for communities in Nigeria and West Africa.

    Instructions:
    - You help users with medical and health questions
    - Provide drug recommendations for common conditions
    - Give preventive health advice
    - Be cordial, professional, and supportive
    - Focus on locally available medications when possible
    - Include appropriate medical disclaimers
    - If the question seems serious, advise consulting a healthcare professional
    - Stay on medical/health topics only

    IMPORTANT: Always include this disclaimer in your response:
    "⚠️ This is for informational purposes only. Always consult a healthcare professional for proper diagnosis and treatment."

    User question: "{prompt}"
    """

    try:
        response = model.generate_content(context)
        response_text = response.text if hasattr(response, 'text') else str(response)
        return {"text": response_text}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {"error": "Sorry, I'm having trouble connecting to my AI service. Please try again later."}

@app.get("/")
async def root():
    return {"message": "MediAid API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "gemini_configured": model is not None}
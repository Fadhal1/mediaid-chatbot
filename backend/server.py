from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Drug(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    generic_name: str
    description: str
    uses: List[str]
    dosage: str
    side_effects: List[str]
    precautions: List[str]
    symptoms: List[str]  # Symptoms this drug can treat
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_message: str
    bot_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    drug_suggestions: List[Drug] = []

# Sample drug data
SAMPLE_DRUGS = [
    {
        "name": "Paracetamol",
        "generic_name": "Acetaminophen",
        "description": "Pain reliever and fever reducer",
        "uses": ["Pain relief", "Fever reduction", "Headache", "Muscle pain"],
        "dosage": "500mg-1000mg every 4-6 hours, max 4000mg/day",
        "side_effects": ["Nausea", "Stomach upset", "Liver damage (overdose)"],
        "precautions": ["Don't exceed maximum dose", "Avoid alcohol", "Check other medications"],
        "symptoms": ["headache", "fever", "pain", "muscle pain", "toothache"]
    },
    {
        "name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "description": "Anti-inflammatory pain reliever",
        "uses": ["Pain relief", "Inflammation reduction", "Fever reduction"],
        "dosage": "200-400mg every 4-6 hours, max 1200mg/day",
        "side_effects": ["Stomach irritation", "Nausea", "Dizziness"],
        "precautions": ["Take with food", "Avoid if stomach ulcers", "Don't exceed dose"],
        "symptoms": ["headache", "fever", "pain", "inflammation", "arthritis", "muscle pain"]
    },
    {
        "name": "Aspirin",
        "generic_name": "Acetylsalicylic acid",
        "description": "Pain reliever and blood thinner",
        "uses": ["Pain relief", "Fever reduction", "Heart protection", "Stroke prevention"],
        "dosage": "325-650mg every 4 hours for pain, 81mg daily for heart protection",
        "side_effects": ["Stomach bleeding", "Nausea", "Heartburn"],
        "precautions": ["Not for children under 16", "Avoid if bleeding disorders", "Take with food"],
        "symptoms": ["headache", "fever", "pain", "heart disease"]
    },
    {
        "name": "Loratadine",
        "generic_name": "Loratadine",
        "description": "Antihistamine for allergies",
        "uses": ["Allergy relief", "Hay fever", "Itching", "Runny nose"],
        "dosage": "10mg once daily",
        "side_effects": ["Drowsiness", "Dry mouth", "Headache"],
        "precautions": ["May cause drowsiness", "Avoid alcohol", "Check drug interactions"],
        "symptoms": ["allergies", "hay fever", "itching", "runny nose", "sneezing"]
    },
    {
        "name": "Omeprazole",
        "generic_name": "Omeprazole",
        "description": "Acid reducer for stomach problems",
        "uses": ["Heartburn", "Acid reflux", "Stomach ulcers", "GERD"],
        "dosage": "20mg once daily before meals",
        "side_effects": ["Headache", "Nausea", "Diarrhea"],
        "precautions": ["Take before meals", "Don't crush tablets", "Long-term use monitoring"],
        "symptoms": ["heartburn", "acid reflux", "stomach pain", "indigestion"]
    },
    {
        "name": "Dextromethorphan",
        "generic_name": "Dextromethorphan",
        "description": "Cough suppressant",
        "uses": ["Dry cough", "Cough relief"],
        "dosage": "15-30mg every 4-8 hours",
        "side_effects": ["Drowsiness", "Dizziness", "Nausea"],
        "precautions": ["Not for productive cough", "Avoid alcohol", "Check other medications"],
        "symptoms": ["cough", "dry cough"]
    },
    {
        "name": "Loperamide",
        "generic_name": "Loperamide",
        "description": "Anti-diarrheal medication",
        "uses": ["Diarrhea treatment", "Bowel movement control"],
        "dosage": "2mg after each loose stool, max 16mg/day",
        "side_effects": ["Constipation", "Nausea", "Drowsiness"],
        "precautions": ["Don't use if fever present", "Don't exceed maximum dose", "Stay hydrated"],
        "symptoms": ["diarrhea", "loose stool", "stomach upset"]
    },
    {
        "name": "Cetirizine",
        "generic_name": "Cetirizine",
        "description": "Antihistamine for allergies",
        "uses": ["Allergy relief", "Seasonal allergies", "Itching", "Hives"],
        "dosage": "10mg once daily",
        "side_effects": ["Drowsiness", "Dry mouth", "Fatigue"],
        "precautions": ["May cause drowsiness", "Avoid alcohol", "Reduce dose in kidney disease"],
        "symptoms": ["allergies", "itching", "hives", "seasonal allergies", "runny nose"]
    }
]

# Health advice patterns
HEALTH_ADVICE = {
    "fever": "For fever: Rest, drink plenty of fluids, use fever reducers like Paracetamol. See a doctor if fever exceeds 103°F (39.4°C) or persists for more than 3 days.",
    "headache": "For headaches: Rest in a quiet, dark room, apply cold or warm compress, stay hydrated. Try Paracetamol or Ibuprofen. See a doctor if severe or recurring.",
    "cough": "For cough: Stay hydrated, use honey, avoid irritants. Use cough suppressants for dry cough. See a doctor if blood in cough or persists over 2 weeks.",
    "diarrhea": "For diarrhea: Stay hydrated with ORS, eat bland foods (BRAT diet), avoid dairy and fatty foods. Use Loperamide if needed. See a doctor if severe or bloody.",
    "allergies": "For allergies: Avoid triggers, use antihistamines like Loratadine or Cetirizine. For severe reactions, seek immediate medical attention.",
    "stomach": "For stomach issues: Eat bland foods, avoid spicy foods, stay hydrated. Use antacids for heartburn. See a doctor if severe pain or blood in stool.",
    "pain": "For pain: Rest, apply ice/heat, use pain relievers like Paracetamol or Ibuprofen. See a doctor if severe or doesn't improve with rest.",
    "general": "Always consult a healthcare provider for persistent symptoms, severe conditions, or if you're unsure about medication use."
}

# Initialize database with sample data
async def init_database():
    # Check if drugs already exist
    existing_drugs = await db.drugs.count_documents({})
    if existing_drugs == 0:
        # Insert sample drugs
        drug_docs = []
        for drug_data in SAMPLE_DRUGS:
            drug = Drug(**drug_data)
            drug_docs.append(drug.dict())
        await db.drugs.insert_many(drug_docs)
        print("Sample drugs inserted into database")

# Simple NLP function for symptom detection
def detect_symptoms(message: str) -> List[str]:
    message_lower = message.lower()
    symptoms = []
    
    # Common symptom patterns
    symptom_patterns = {
        "headache": ["headache", "head ache", "head pain", "migraine"],
        "fever": ["fever", "temperature", "hot", "burning up"],
        "cough": ["cough", "coughing", "throat", "chest congestion"],
        "pain": ["pain", "ache", "hurt", "sore"],
        "diarrhea": ["diarrhea", "loose stool", "stomach runs", "loose motion"],
        "allergies": ["allergy", "allergic", "itching", "runny nose", "sneezing"],
        "stomach": ["stomach", "tummy", "belly", "indigestion", "heartburn"],
        "muscle pain": ["muscle", "body ache", "joint pain", "stiff"]
    }
    
    for symptom, patterns in symptom_patterns.items():
        if any(pattern in message_lower for pattern in patterns):
            symptoms.append(symptom)
    
    return symptoms

# Chatbot response function
async def generate_response(message: str) -> ChatResponse:
    message_lower = message.lower()
    
    # Detect symptoms
    symptoms = detect_symptoms(message)
    
    # Find relevant drugs
    drug_suggestions = []
    if symptoms:
        for symptom in symptoms:
            drugs_cursor = db.drugs.find({"symptoms": {"$in": [symptom]}})
            drugs = await drugs_cursor.to_list(length=10)
            for drug_data in drugs:
                drug = Drug(**drug_data)
                if drug not in drug_suggestions:
                    drug_suggestions.append(drug)
    
    # Generate response
    if not symptoms:
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "good morning", "good evening"]):
            response = "Hello! I'm MediAid, your local health assistant. I can help you with information about medications and basic health advice. What symptoms are you experiencing?"
        elif any(drug_query in message_lower for drug_query in ["what is", "tell me about", "medicine", "drug"]):
            response = "I can help you with information about medications! Please tell me the name of the drug you're asking about, or describe your symptoms and I'll suggest appropriate medications."
        else:
            response = "I can help you with health advice and medication information. Please describe your symptoms or ask about a specific medication."
    else:
        response_parts = []
        for symptom in symptoms:
            if symptom in HEALTH_ADVICE:
                response_parts.append(HEALTH_ADVICE[symptom])
        
        if response_parts:
            response = "\n\n".join(response_parts)
        else:
            response = HEALTH_ADVICE["general"]
        
        if drug_suggestions:
            response += f"\n\nI found {len(drug_suggestions)} medication(s) that might help with your symptoms. Check the suggestions below for more details."
    
    return ChatResponse(response=response, drug_suggestions=drug_suggestions)

# Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate response
        chat_response = await generate_response(request.message)
        
        # Save to database
        chat_message = ChatMessage(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=chat_response.response
        )
        await db.chat_messages.insert_one(chat_message.dict())
        
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/drugs", response_model=List[Drug])
async def get_drugs(symptom: Optional[str] = None):
    try:
        if symptom:
            drugs_cursor = db.drugs.find({"symptoms": {"$in": [symptom.lower()]}})
        else:
            drugs_cursor = db.drugs.find()
        
        drugs = await drugs_cursor.to_list(length=100)
        return [Drug(**drug) for drug in drugs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/drugs/{drug_id}", response_model=Drug)
async def get_drug(drug_id: str):
    try:
        drug = await db.drugs.find_one({"id": drug_id})
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return Drug(**drug)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/search", response_model=List[Drug])
async def search_drugs(query: str):
    try:
        # Search in drug names, symptoms, and uses
        search_pattern = {"$regex": query, "$options": "i"}
        drugs_cursor = db.drugs.find({
            "$or": [
                {"name": search_pattern},
                {"generic_name": search_pattern},
                {"symptoms": search_pattern},
                {"uses": search_pattern}
            ]
        })
        
        drugs = await drugs_cursor.to_list(length=50)
        return [Drug(**drug) for drug in drugs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        messages_cursor = db.chat_messages.find({"session_id": session_id}).sort("timestamp", 1)
        messages = await messages_cursor.to_list(length=100)
        return [ChatMessage(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
# MediAid - Health Companion

>MediAid is a web-based health chatbot that provides instant drug recommendations and preventive health advice for common conditions. It uses a local dataset and can fall back to Google Gemini AI for professional, friendly answers.

## Features
- Chatbot interface for health questions
- Local dataset for fast, offline answers
- Gemini AI fallback for broader health advice
- Modern, mobile-friendly UI (Tailwind CSS)

## How to Run Locally

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Fadhal1/mediaid.git
   cd mediaid
   ```
2. **Install Python dependencies:**
   ```sh
   python -m pip install -r requirements.txt
   ```
   (Or manually install: `fastapi`, `uvicorn`, `google-generativeai`)
3. **Set your Gemini API key:**
   - Edit `main.py` and set your API key, or use an environment variable.
4. **Start the backend:**
   ```sh
   python -m uvicorn "New folder.main":app --reload
   ```
5. **Serve the frontend:**
   ```sh
   python -m http.server 8080
   ```
   Then open [http://localhost:8080/index.html](http://localhost:8080/index.html)

## Deployment
- Remove your API key before pushing to GitHub.
- Use environment variables for secrets in production.
- You can deploy the backend to platforms like Render, Railway, or Fly.io.

## Folder Structure
- `index.html` - Main frontend
- `main.py` - FastAPI backend (in `New folder/`)
- `mediaid-logo.png` - Logo
- `mediaid_full_dataset.json` - Local health dataset (optional/private)
- `.gitignore` - Excludes venv, cache, and secrets

## License
MIT

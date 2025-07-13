# MediAid - Health Companion

> MediAid is a web-based health chatbot that provides instant drug recommendations and preventive health advice for common conditions. It uses a local dataset and can fall back to Google Gemini AI for professional, friendly answers.

## Features
- Chatbot interface for health questions
- Local dataset for fast, offline answers
- Gemini AI fallback for broader health advice
- Modern, mobile-friendly UI (Tailwind CSS)

## Prerequisites
- Python 3.8 or higher
- Google Gemini API key

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Fadhal1/mediaid.git
cd mediaid
```

### 2. Set up Python environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

### 5. Run the application

**Start the backend:**
```bash
python main.py
```
The API will be available at `http://localhost:8000`

**Serve the frontend:**
```bash
python -m http.server 8080
```
Then open [http://localhost:8080/index.html](http://localhost:8080/index.html)

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check with configuration status
- `POST /api/ai` - AI chat endpoint

## Deployment

### Environment Variables for Production
- `GEMINI_API_KEY` - Your Gemini API key

### Recommended Platforms
- **Backend**: Render, Railway, Fly.io, or Heroku
- **Frontend**: Netlify, Vercel, or GitHub Pages

### Deployment Steps
1. Push your code to GitHub (API key will be ignored due to .gitignore)
2. Deploy backend to your chosen platform
3. Set the `GEMINI_API_KEY` environment variable in your deployment platform
4. Deploy frontend and update the API URL in `index.html`

## Project Structure
```
mediaid/
├── main.py                 # FastAPI backend
├── index.html             # Frontend interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── mediaid-logo.png      # Logo file
└── mediaid_full_dataset.json  # Local health dataset
```

## Troubleshooting

### Backend Issues
- **"Gemini API not configured"**: Check if your API key is set in the `.env` file
- **CORS errors**: Make sure the backend is running on port 8000
- **Module not found**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Frontend Issues
- **"Error contacting AI service"**: Check if the backend is running and accessible
- **Dataset not loaded**: Ensure `mediaid_full_dataset.json` exists in the root directory

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
MIT License

## Support
If you encounter any issues, please create an issue on the GitHub repository.

---
**⚠️ Important**: Never commit your actual API key to version control. Always use environment variables for sensitive information.
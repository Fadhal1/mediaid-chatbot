# File: /api/chat.py
import os
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import json

# This is a simple HTTP request handler that Vercel can run as a serverless function.
class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # Get the API key from the Vercel environment variables
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "GEMINI_API_KEY is not set."}).encode('utf-8'))
                return
            
            genai.configure(api_key=api_key)

            # Get the prompt from the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_body = json.loads(post_data)
            prompt = request_body.get('prompt')

            if not prompt:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Prompt is required."}).encode('utf-8'))
                return
            
            # Call the Gemini API
            model = genai.GenerativeModel('gemini-pro') # Using gemini-pro is standard for chat
            response = model.generate_content(prompt)

            # Send the response back to the frontend
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = json.dumps({"reply": response.text})
            self.wfile.write(response_data.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        
        return

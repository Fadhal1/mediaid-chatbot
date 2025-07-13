#!/usr/bin/env python3
"""
Development script to run MediAid locally
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "main.py",
        "index.html",
        "requirements.txt",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        if ".env" in missing_files:
            print("📝 Please copy .env.example to .env and add your Gemini API key")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    try:
        # Start the backend in a separate process
        backend_process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if the process is still running
        if backend_process.poll() is None:
            print("✅ Backend server started successfully at http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting frontend server...")
    try:
        # Start the frontend in a separate process
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "8080"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(2)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started successfully at http://localhost:8080")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main function to run the development environment"""
    print("🏥 MediAid Development Server")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    # Open browser
    print("🌍 Opening browser...")
    webbrowser.open("http://localhost:8080/index.html")
    
    print("\n✅ MediAid is running!")
    print("📱 Frontend: http://localhost:8080/index.html")
    print("🔧 Backend API: http://localhost:8000")
    print("❤️ Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the servers...")
    
    try:
        # Wait for user interruption
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped successfully")

if __name__ == "__main__":
    main()
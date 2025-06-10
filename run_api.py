#!/usr/bin/env python3
"""
ARQA API Launcher
Simple script to run the FastAPI server with proper imports
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the API
try:
    from src.arqa.api_optimized import app
except ImportError:
    from src.arqa.api import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting ARQA API Server...")    
    print(f"📁 Project root: {project_root}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=False
    )

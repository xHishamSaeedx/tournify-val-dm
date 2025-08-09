#!/usr/bin/env python3
"""
Startup script for the Tournify Valorant DM API.
This script provides an easy way to run the FastAPI application.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Tournify Valorant DM API...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

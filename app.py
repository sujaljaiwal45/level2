"""
Main entry point for Hugging Face Spaces deployment.

CHANGES FOR HUGGING FACE SPACES:
1. This file is required by Hugging Face Spaces - it looks for app.py or main.py
2. The app runs on the PORT environment variable (defaults to 7860)
3. Uses uvicorn to serve the FastAPI application
"""

import os
import uvicorn
from api import app

# Hugging Face Spaces sets the PORT environment variable
# Default to 8000 for localhost, 7860 for Hugging Face Spaces
port = int(os.environ.get("PORT", 8000))

# Host must be 0.0.0.0 for Hugging Face Spaces to access it
host = "0.0.0.0"

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)

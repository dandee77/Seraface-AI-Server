#!/usr/bin/env python3
"""
Seraface AI Server - Entry Point

This is the main entry point for the Seraface AI Server application.
Run this file to start the FastAPI server.

Usage:
    python main.py
    python -m uvicorn main:app --reload  # For development
"""

from app import app
from app.core import settings

def main():
    """Main entry point for the application"""
    import uvicorn
    uvicorn.run(
        "main:app",  # Use string reference for auto-reload
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )

if __name__ == "__main__":
    main()

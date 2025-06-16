#!/usr/bin/env python3
"""
Risk Tracker Application Startup Script
"""

import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 Starting Risk Tracker Application...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🐛 Debug mode: {debug}")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("---")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    ) 
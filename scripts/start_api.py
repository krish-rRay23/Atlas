"""Launch script for ATLAS FastAPI REST API."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from atlas.core.config import settings
from atlas.core.db import init_database

if __name__ == "__main__":
    init_database()
    print(f"Starting ATLAS API on http://{settings.api_host}:{settings.api_port}")
    uvicorn.run("atlas.api.main:app", host=settings.api_host, port=settings.api_port, reload=False)

"""ATLAS Configuration & Environment Management.

Evidence. Intelligence. Decisions.
"""

from pathlib import Path
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
BENCHMARK_DATA_DIR = DATA_DIR / "benchmarks"
EVALUATION_DATA_DIR = DATA_DIR / "evaluation"

# Database paths
SQLITE_DB_PATH = DATA_DIR / "atlas.db"
DUCKDB_PATH = DATA_DIR / "atlas_analytics.duckdb"

# Target economies
TARGET_ECONOMIES = {
    "IND": {"name": "India", "region": "South Asia", "currency": "INR", "central_bank": "Reserve Bank of India (RBI)"},
    "IDN": {"name": "Indonesia", "region": "Southeast Asia", "currency": "IDR", "central_bank": "Bank Indonesia (BI)"},
    "VNM": {"name": "Vietnam", "region": "Southeast Asia", "currency": "VND", "central_bank": "State Bank of Vietnam (SBV)"},
    "THA": {"name": "Thailand", "region": "Southeast Asia", "currency": "THB", "central_bank": "Bank of Thailand (BOT)"},
    "PHL": {"name": "Philippines", "region": "Southeast Asia", "currency": "PHP", "central_bank": "Bangko Sentral ng Pilipinas (BSP)"},
}

# API and Model configuration
class Settings(BaseModel):
    app_name: str = "ATLAS — Asia Research Evidence Intelligence & Decision Workbench"
    version: str = "1.0.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    ui_port: int = 8501
    
    # Environment keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_api_base: Optional[str] = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    anthropic_auth_token: Optional[str] = os.getenv("ANTHROPIC_AUTH_TOKEN")
    anthropic_base_url: Optional[str] = os.getenv("ANTHROPIC_BASE_URL")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    # Provider selection: 'openai', 'anthropic', 'gemini', or 'deterministic'
    model_provider: str = os.getenv("ATLAS_MODEL_PROVIDER", "auto")

settings = Settings()


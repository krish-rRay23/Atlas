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
    environment: str = os.getenv("ATLAS_ENV", "development")
    api_host: str = os.getenv("ATLAS_API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("ATLAS_API_PORT", 8000))
    ui_port: int = int(os.getenv("ATLAS_UI_PORT", 8501))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH}")
    duckdb_path: str = str(DUCKDB_PATH)
    
    # Security & Auth
    auth_enabled: bool = os.getenv("ATLAS_AUTH_ENABLED", "false").lower() in ("true", "1", "yes")
    secret_key: str = os.getenv("ATLAS_SECRET_KEY", "atlas-enterprise-dev-secret-key-change-in-prod-2026")
    allowed_cors_origins: list = [
        "http://localhost:8501", "http://127.0.0.1:8501",
        "http://localhost:8000", "http://127.0.0.1:8000"
    ]
    api_key_header_name: str = "X-ATLAS-API-KEY"
    admin_api_key: str = os.getenv("ATLAS_ADMIN_API_KEY", "atlas-admin-dev-key")
    researcher_api_key: str = os.getenv("ATLAS_RESEARCHER_API_KEY", "atlas-researcher-dev-key")
    reviewer_api_key: str = os.getenv("ATLAS_REVIEWER_API_KEY", "atlas-reviewer-dev-key")
    reader_api_key: str = os.getenv("ATLAS_READER_API_KEY", "atlas-reader-dev-key")
    
    # Environment keys for LLMs
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
    
    # Pricing configuration (per 1,000,000 tokens)
    pricing_catalog: dict = {
        "gemini-2.5-flash-lite": {"input_per_m": 0.10, "output_per_m": 0.40},
        "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-1.5-pro": {"input_per_m": 1.25, "output_per_m": 5.00},
        "gpt-4o-mini": {"input_per_m": 0.15, "output_per_m": 0.60},
        "claude-3-5-sonnet-20241022": {"input_per_m": 3.00, "output_per_m": 15.00}
    }
    
    # Background Workers & Timeouts
    job_timeout_seconds: int = 300
    max_request_size_bytes: int = 10 * 1024 * 1024  # 10 MB

settings = Settings()


"""
config.py — Central configuration loader for SmartFarmingAI.
All secrets are read exclusively from environment variables / .env file.
NEVER hardcode credentials here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent / ".env")


class Config:
    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")
    ENV: str = os.environ.get("FLASK_ENV", "production")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    PORT: int = int(os.environ.get("FLASK_PORT", 5000))

    # ── IBM watsonx.ai ──────────────────────────────────────────────────────
    IBM_API_KEY: str = os.environ.get("IBM_API_KEY", "")
    IBM_PROJECT_ID: str = os.environ.get("IBM_PROJECT_ID", "")
    IBM_WATSONX_URL: str = os.environ.get(
        "IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
    )

    # ── Granite Models ──────────────────────────────────────────────────────
    GRANITE_INSTRUCT_MODEL: str = os.environ.get(
        "GRANITE_INSTRUCT_MODEL", "ibm/granite-3-8b-instruct"
    )
    GRANITE_VISION_MODEL: str = os.environ.get(
        "GRANITE_VISION_MODEL", "ibm/granite-vision-3-2-2b"
    )
    GRANITE_EMBEDDING_MODEL: str = os.environ.get(
        "GRANITE_EMBEDDING_MODEL", "ibm/granite-embedding-30m-english"
    )

    # ── Granite inference parameters ────────────────────────────────────────
    GRANITE_MAX_TOKENS: int = 1024
    GRANITE_TEMPERATURE: float = 0.7
    GRANITE_TOP_P: float = 0.95

    # ── Weather API ──────────────────────────────────────────────────────────
    WEATHER_API_KEY: str = os.environ.get("WEATHER_API_KEY", "")
    WEATHER_BASE_URL: str = os.environ.get(
        "WEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5"
    )

    # ── Database ──────────────────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).parent
    DATABASE_PATH: Path = BASE_DIR / "database" / "smartfarming.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    CHROMA_DB_PATH: str = os.environ.get("CHROMA_DB_PATH", "./database/chroma_db")
    CHROMA_COLLECTION_NAME: str = os.environ.get(
        "CHROMA_COLLECTION_NAME", "farming_knowledge"
    )

    # ── File Uploads ──────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "./uploads")
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}

    # ── Reports ───────────────────────────────────────────────────────────────
    REPORTS_FOLDER: str = os.environ.get("REPORTS_FOLDER", "./reports")

    # ── Knowledge Base ────────────────────────────────────────────────────────
    KNOWLEDGE_BASE_PATH: str = str(BASE_DIR / "data" / "knowledge_base")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # ── Session ────────────────────────────────────────────────────────────────
    SESSION_TYPE: str = "filesystem"
    SESSION_PERMANENT: bool = False
    SESSION_USE_SIGNER: bool = True

    @classmethod
    def validate(cls) -> None:
        """Raise ValueError if critical env vars are missing."""
        missing = []
        for var in ("IBM_API_KEY", "IBM_PROJECT_ID"):
            if not getattr(cls, var):
                missing.append(var)
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please set them in your .env file."
            )


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

ActiveConfig = config_map.get(os.environ.get("FLASK_ENV", "development"), DevelopmentConfig)

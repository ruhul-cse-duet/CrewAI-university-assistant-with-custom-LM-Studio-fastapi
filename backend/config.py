import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Enhanced Configuration for University AI Assistant"""
    
    # LM Studio Configuration
    LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "")
    LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_VERSION = "v1"
    
    # Google Search API (Free alternatives: SerpAPI, ScraperAPI)
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    USE_SERPER_API = os.getenv("USE_SERPER_API", "true").lower() == "true"
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    
    # University Configuration (Required in .env)
    UNIVERSITY_DOMAIN_RAW = os.getenv("UNIVERSITY_DOMAIN", "")
    # Clean domain - remove protocol and www
    if UNIVERSITY_DOMAIN_RAW:
        # Remove https:// or http://
        domain = UNIVERSITY_DOMAIN_RAW.replace("https://", "").replace("http://", "")
        # Remove www. prefix
        domain = domain.replace("www.", "")
        # Remove trailing slash
        domain = domain.rstrip("/")
        UNIVERSITY_DOMAIN = domain.strip()
        # Extract university name from domain if not provided
        UNIVERSITY_NAME = os.getenv("UNIVERSITY_NAME", UNIVERSITY_DOMAIN.split('.')[0].upper())
    else:
        UNIVERSITY_DOMAIN = ""
        UNIVERSITY_NAME = os.getenv("UNIVERSITY_NAME", "University")
    
    # Official domains to whitelist (only add if domain is provided)
    OFFICIAL_DOMAINS: List[str] = []
    if UNIVERSITY_DOMAIN and UNIVERSITY_DOMAIN.strip():
        OFFICIAL_DOMAINS = [
            UNIVERSITY_DOMAIN,
            f"www.{UNIVERSITY_DOMAIN}",
            f"portal.{UNIVERSITY_DOMAIN}",
            f"notice.{UNIVERSITY_DOMAIN}",
            f"library.{UNIVERSITY_DOMAIN}",
        ]
    
    # FAISS & Embeddings Configuration
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    METADATA_PATH = os.getenv("METADATA_PATH", "./data/metadata.json")
    
    # Embedding Model Configuration
    # Always use HuggingFace multilingual sentence transformer for Bengali/English support
    EMBEDDING_PROVIDER = "sentence-transformers"  # Fixed to use HuggingFace multilingual
    
    # HuggingFace multilingual sentence transformer (supports Bengali and English)
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )
    
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))
    
    # Search Configuration
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", 10))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.5))
    
    # Cache Settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", 24))
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 1000))
    
    # Scraping Configuration
    SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", 10))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 1000))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 200))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", 60))
    
    # Language Settings
    SUPPORTED_LANGUAGES = ["bn", "en"]
    DEFAULT_LANGUAGE = "bn"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    # CORS Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Cloud Deployment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database (Optional - for future expansion)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
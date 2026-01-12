from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import logging
from datetime import datetime
import time
from collections import defaultdict
import asyncio

from router import QueryRouter
from config import Config
from tools.faiss_store import FAISSStore

# Configure logging with UTF-8 encoding for Windows compatibility
import sys
if sys.platform == 'win32':
    # Fix Windows console encoding for Unicode
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="🎓 University AI Assistant API",
    description="Multi-agent AI system for university information with Google Search integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include notice routes


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
rate_limit_store = defaultdict(list)

def check_rate_limit(request: Request):
    """Simple rate limiting"""
    if not Config.RATE_LIMIT_ENABLED:
        return True
    
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if current_time - req_time < Config.RATE_LIMIT_PERIOD
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= Config.RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return True

# Initialize components (lazy loading - models load on first use)
# Make initialization non-blocking - allow app to start even if some components fail
query_router = None
faiss_store = None

def initialize_components():
    """Initialize components with error handling"""
    global query_router, faiss_store
    try:
        logger.info("Initializing application components (fast startup)...")
        faiss_store = FAISSStore()
        logger.info("FAISS store initialized")
    except Exception as e:
        logger.error(f"FAISS store initialization error: {str(e)}", exc_info=True)
        faiss_store = None
    
    try:
        # Pass faiss_store to QueryRouter to avoid duplicate initialization
        query_router = QueryRouter(faiss_store=faiss_store)
        logger.info("Query router initialized")
    except Exception as e:
        logger.error(f"Query router initialization error: {str(e)}", exc_info=True)
        query_router = None
    
    if query_router:
        logger.info("Application initialized successfully (models will load on first query)")
    else:
        logger.warning("Query router failed to initialize - app will start but queries may fail")

# Initialize components
initialize_components()

# Pydantic Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User question")
    language: Optional[str] = Field("bn", description="Language: 'bn' or 'en'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "আজকের নোটিশ কী?",
                "language": "bn"
            }
        }

class QueryResponse(BaseModel):
    success: bool
    answer: str
    agent: str
    source: str
    timestamp: str
    processing_time_ms: float
    results: Optional[List[dict]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    faiss_stats: dict
    timestamp: str

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if Config.DEBUG else "An error occurred"
        }
    )

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - always works, doesn't require initialization"""
    return {
        "message": "🎓 University AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running" if query_router else "initializing"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint (fast, doesn't load models)"""
    try:
        # Get stats without loading embedding model
        faiss_stats = {}
        if faiss_store:
            try:
                faiss_stats = faiss_store.get_stats()
            except Exception as e:
                # If model not loaded yet, return basic stats
                logger.debug(f"FAISS stats not available yet: {str(e)}")
                faiss_stats = {"status": "initializing", "total_documents": 0}
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            environment=Config.ENVIRONMENT,
            faiss_stats=faiss_stats,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def process_query(request: Request, query_request: QueryRequest):
    """
    Process user query following complete workflow:
    1. Search Google
    2. Filter URLs
    3. Scrape content
    4. Store in FAISS
    5. Semantic search
    6. Generate answer
    """
    start_time = time.time()
    
    # Rate limiting
    if not check_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Validate components
    if not query_router:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized properly"
        )
    
    try:
        logger.info(f"Processing query: {query_request.query}")
        
        # Run query processing in executor to avoid blocking
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        # Use thread pool for CPU-bound operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # Set timeout to prevent hanging
            future = loop.run_in_executor(
                executor,
                query_router.route_query,
                query_request.query,
                query_request.language
            )
            # Wait with timeout (180 seconds max)
            result = await asyncio.wait_for(future, timeout=300.0)
        
        processing_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            success=result['success'],
            answer=result['answer'],
            agent=result['agent'],
            source=result['source'],
            timestamp=datetime.now().isoformat(),
            processing_time_ms=round(processing_time, 2),
            results=result.get('results', [])
        )
        
    except asyncio.TimeoutError:
        logger.error(f"Query timeout after 180 seconds: {query_request.query}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Query processing timeout. Please try a simpler question or try again later."
        )
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) if Config.DEBUG else "An error occurred processing your query"
        )

@app.get("/stats", tags=["Statistics"])
async def get_stats():
    """Get system statistics"""
    try:
        return {
            "faiss": faiss_store.get_stats() if faiss_store else {},
            "config": {
                "university": Config.UNIVERSITY_NAME,
                "domain": Config.UNIVERSITY_DOMAIN,
                "cache_enabled": Config.CACHE_ENABLED,
                "rate_limit": Config.RATE_LIMIT_ENABLED
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/clear", tags=["Cache"])
async def clear_cache():
    """Clear FAISS cache (admin only)"""
    try:
        if faiss_store:
            faiss_store.clear_index()
            return {"success": True, "message": "Cache cleared"}
        return {"success": False, "message": "FAISS store not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting University AI Assistant API...")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"University: {Config.UNIVERSITY_NAME}")
    logger.info(f"Debug mode: {Config.DEBUG}")

# Main backend/app.py
if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            "app:app",  # When running from backend directory, use app:app
            host=Config.API_HOST,
            port=Config.API_PORT,
            reload=Config.DEBUG,
            log_level=Config.LOG_LEVEL.lower(),
            access_log=False,  # Reduce logging overhead
            timeout_keep_alive=60
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise

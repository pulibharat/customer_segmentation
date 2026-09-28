"""
Customer Support Agent with Hindsight Memory
FastAPI application entry point
"""

from app.api.routes import memory_client, router as api_router
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Agent with Hindsight",
    description="AI-powered support agent with persistent memory using Hindsight",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint


@app.get("/health")
async def health_check():
    """Simple health check for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "customer_support_agent",
        "version": "1.0.0"
    }

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "name": "Customer Support Agent with Hindsight Memory",
        "description": "AI support agent demonstrating persistent memory for learning and improvement",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

# Startup event


@app.on_event("startup")
async def startup_event():
    logger.info("Customer Support Agent starting up...")
    # Initialize Hindsight connection here if needed
    logger.info("Application initialized successfully")

# Shutdown event


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Customer Support Agent shutting down...")
    await memory_client.close()

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

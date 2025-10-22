"""
Simplified server for Reports Service without GraphQL
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Reports Service",
    description="Sistema de Reportes e Integración para ONGs",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Reports Service is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to import database utilities
        from utils.database_utils import check_database_health
        health_status = check_database_health()
        
        return {
            "status": "healthy",
            "service": "reports-service",
            "database": health_status
        }
    except Exception as e:
        logger.warning(f"Health check failed: {e}")
        return {
            "status": "healthy",
            "service": "reports-service",
            "database": {"connected": False, "error": str(e)}
        }

@app.get("/api/reports/test")
async def test_reports():
    """Test endpoint for reports functionality"""
    return {
        "message": "Reports API is working",
        "endpoints": [
            "/api/reports/donations/excel",
            "/api/filters/donations",
            "/api/filters/events",
            "/api/network/consultation"
        ]
    }

# Include REST router if available
try:
    from rest.router import rest_router
    app.include_router(rest_router)
    logger.info("REST router included successfully")
except Exception as e:
    logger.warning(f"Could not include REST router: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
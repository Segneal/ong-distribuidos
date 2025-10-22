#!/usr/bin/env python3
"""
Simple startup script for Reports Service
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Create FastAPI app
app = FastAPI(
    title="Reports Service",
    description="Sistema de Reportes e Integración para ONGs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Reports Service is running", 
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reports-service",
        "version": "1.0.0"
    }

@app.get("/api/reports/test")
async def test_reports():
    """Test endpoint for reports functionality"""
    return {
        "message": "Reports API is working",
        "available_endpoints": [
            "GET /",
            "GET /health", 
            "GET /api/reports/test"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Reports Service...")
    print("📊 Service will be available at: http://localhost:8002")
    print("🔍 Health check: http://localhost:8002/health")
    print("🧪 Test endpoint: http://localhost:8002/api/reports/test")
    
    uvicorn.run(
        "start_server:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )
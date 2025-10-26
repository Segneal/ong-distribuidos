#!/usr/bin/env python3
"""
Main server entry point for Reports Service
Consistent with other services in the system
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

def main():
    """Main entry point"""
    print("🚀 Starting Reports Service...")
    print("📊 Service will be available at: http://localhost:8002")
    print("🔍 Health check: http://localhost:8002/health")
    
    try:
        # Try to import and run the original GraphQL server with database
        from src.main import app
        print("✅ Loading original GraphQL server with database...")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            reload=False
        )
        
    except ImportError as e:
        print(f"⚠️  Graphene GraphQL not available: {e}")
        print("🔄 Trying original GraphQL server...")
        
        try:
            # Try original Strawberry server
            from src.main import app
            print("✅ Loading Strawberry GraphQL server...")
            
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8002,
                reload=False
            )
            
        except ImportError as e2:
            print(f"⚠️  Strawberry GraphQL dependencies not available: {e2}")
            print("🔄 Falling back to simple server...")
        
        # Fallback to simple server without GraphQL
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Reports Service (Simple Mode)",
            description="Sistema de Reportes - Modo Simple",
            version="1.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {
                "message": "Reports Service is running in simple mode", 
                "version": "1.0.0",
                "status": "healthy",
                "mode": "simple"
            }
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "reports-service",
                "version": "1.0.0",
                "mode": "simple"
            }
        
        @app.get("/api/reports/test")
        async def test_reports():
            return {
                "message": "Reports API is working in simple mode",
                "available_endpoints": [
                    "GET /",
                    "GET /health", 
                    "GET /api/reports/test"
                ]
            }
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            reload=False
        )

if __name__ == "__main__":
    main()
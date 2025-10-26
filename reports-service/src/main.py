"""
Main application entry point for the Reports Service
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from strawberry.fastapi import GraphQLRouter
from src.config import settings
from src.models import init_database
from src.utils.database_utils import check_database_health
from src.gql.schema import schema
from src.gql.context import get_graphql_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Reports Service...")
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Reports Service...")

# Create FastAPI application
app = FastAPI(
    title="Reports Service",
    description="Sistema de Reportes e Integración para ONGs",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
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
    """Comprehensive health check endpoint"""
    health_status = check_database_health()
    
    if not health_status["database_connected"]:
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    return {
        "status": "healthy",
        "service": "reports-service",
        "database": health_status
    }

# Configure GraphQL router
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_graphql_context,
    path="/graphql"
)

# Include GraphQL router
app.include_router(graphql_app, prefix="/api")

# Include REST router
from src.rest.router import rest_router
app.include_router(rest_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
"""
Main REST API router that combines all REST endpoints.
"""
from fastapi import APIRouter
from .routes.excel_export import router as excel_router
from .routes.filter_management import router as filter_router
from .routes.network_consultation import router as network_router

# Create main REST router
rest_router = APIRouter()

# Include all route modules
rest_router.include_router(excel_router)
rest_router.include_router(filter_router)
rest_router.include_router(network_router)
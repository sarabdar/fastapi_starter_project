"""
CORS (Cross-Origin Resource Sharing) configuration.

This module provides CORS middleware configuration for the FastAPI application.
"""
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def add_cors_middleware(app):
    """
    Add CORS middleware to the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        FastAPI: The application with CORS middleware configured
    """
    # Use configured origins from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
        expose_headers=["Content-Disposition"],
        max_age=1000,
    )
    
    return app

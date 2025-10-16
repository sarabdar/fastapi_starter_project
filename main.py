from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app.core.config import settings
from app.core.logger import get_logger
from app.api import api_router

from app.core.cors import add_cors_middleware
import uvicorn 


# Only if you need scheduler
# from app.core.scheduler import scheduler_manager

# Import error handlers
from app.core.error_handlers import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Starter Project",
    description="A starter Project for FastAPI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)




# Add CORS middleware using configuration from app.core.cors
app = add_cors_middleware(app)




# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routers
app.include_router(api_router, prefix="/api")


# ==================== APPLICATION LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initialize scheduler and other startup tasks.
    """
    try:
        logger.info("="*60)
        logger.info("Starting Shop Direct Backend...")
        logger.info("="*60)
        
        # Start the scheduler only if its needed otherwise delete this code
        # if settings.ENABLE_SCHEDULER:
        #     await scheduler_manager.start()
        #     logger.info("Scheduler started successfully")
        # else:
        #     logger.info("Scheduler disabled (using Azure WebJobs or external scheduler)")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.exception("Error during application startup: %s", str(e))
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Gracefully shutdown scheduler and cleanup resources.
    """
    try:
        logger.info("="*60)
        logger.info("Shutting down Shop Direct Backend...")
        logger.info("="*60)
        
        # Shutdown the scheduler only if it was enabled
        # if settings.ENABLE_SCHEDULER:
        #     await scheduler_manager.shutdown(wait=True)
        #     logger.info("Scheduler shutdown completed")
        
        # logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.exception("Error during application shutdown: %s", str(e))

@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"status": "ok", "message": "FASTAPI Project is Running!", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "message": "All systems operational"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {"status": "API is running", "endpoints": "/docs for API documentation"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
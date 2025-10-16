from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

# Create the main API router
api_router = APIRouter()    

# Include all versioned API routers
api_router.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])

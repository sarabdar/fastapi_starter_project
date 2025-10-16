from fastapi import APIRouter



from app.api.v1.auth import router as auth_router

# Create the API v1 router
v1_router = APIRouter()

# Include all versioned API routers
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])


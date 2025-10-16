from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from datetime import timedelta
import uuid
from uuid import UUID

# Import models and schemas
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse

# Security and config
from app.core.security import create_access_token, get_current_user
from app.core.config import settings

# Rate limiting and error handling
from app.core.rate_limiter import rate_limit_auth
from app.core.error_handlers import (
    AuthenticationError,
    AuthorizationError,
    ValidationError as AppValidationError,
    ConflictError
)
from app.core.logger import get_logger



router = APIRouter()
logger = get_logger(__name__)



# Applied rate limiting to login endpoint
@router.post("/login", dependencies=[Depends(rate_limit_auth)], responses={
    200: {
        "description": "Successful login",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                    }
                }
            }
        }
    },
    401: {"description": "Invalid credentials or insufficient permissions"},
    403: {"description": "Access denied. Invalid user role"},
    429: {"description": "Too many login attempts. Please try again later."}
})
async def login(login_data: LoginRequest):
    """
    Authenticate a user and retrieve an access token.
    
    **Rate Limited: 5 attempts per 5 minutes**
    
    ## Request Body
    - **email**: User's email address (required)
    - **password**: User's password (required)
    
    ## Returns
    - **access_token**: JWT token for authenticated requests
    - **token_type**: Type of token (always 'bearer')
    - **user**: Object containing user details (id, email, role, name, phone_number)
    
    ## Possible Responses
    - **200**: Successfully authenticated
    - **401**: Invalid credentials or authentication failed
    - **403**: User role not authorized to access the system
    - **429**: Too many login attempts (rate limit exceeded)
    """
    try:
        # Validate login data
        if not login_data.email or not login_data.password:
            raise AuthenticationError("Email and password are required")
        
        # Authenticate user
        # Check DB or whatever your logic is
        # Example: user = await db.get_user_by_email(login_data.email)
        
        # Check if authentication was successful 
        # If not then raise the appropriate custom error
        # The custom error handlers in main.py will automatically catch and format these
        
        # Example error scenarios:
        # if not user:
        #     raise AuthenticationError("Invalid email or password")
        # 
        # if not verify_password(login_data.password, user.hashed_password):
        #     raise AuthenticationError("Invalid email or password")
        #
        # if user.role not in ["admin", "manager"]:
        #     raise AuthorizationError("Access denied. Invalid user role")
        
        #----------------------------------------------
        #----------------------------------------------
        # Verify password of user whereever you saved it
        #----------------------------------------------
        #----------------------------------------------

        # Then you will get a user id from your DB
        # Use that for creating JWT token
        # For Demo
        user_id = str(uuid.uuid4())

        
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


        
        # Create response using the LoginResponse schema
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
                id=UUID(user_id),
                email=login_data.email,
                # Add other user fields as they become available
                # role="user",
                # name="User Name",
                # phone_number="+1234567890"
            )
        )
    
    except (AuthenticationError, AuthorizationError):
        # Re-raise custom errors - they will be caught by the custom error handlers in main.py
        # No need to convert to HTTPException, the handlers do that automatically
        raise
    
    except Exception as e:
        # Log unexpected errors and raise a generic error
        logger.error(f"Unexpected error during login: {str(e)}")
        raise AuthenticationError("An unexpected error occurred during login")
    
    
    
@router.get(
    "/me", 
    responses={
        200: {
            "description": "Successfully retrieved current user information",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                        }
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"}
    }
)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    
    Returns:
        UserInResponse: The authenticated user's information wrapped in a response object.
        
    Raises:
        HTTPException: If user is not authenticated or token is invalid.
    """
    
    # Create a User model instance and wrap it in UserInResponse
    return JSONResponse(content={"user": {"id": str(current_user.get("sub"))}}, status_code=status.HTTP_200_OK)

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class Token(BaseModel):
    """Schema for the access token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user data in the login response."""
    id: UUID
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request body."""
    email: EmailStr
    password: str


class LoginResponse(Token):
    """Schema for the login response containing access token and user data."""
    user: UserResponse
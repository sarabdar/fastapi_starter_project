from pydantic import BaseModel




class User(BaseModel):
    """Response model for user."""
    id: str
    # Add more 


class UserInResponse(BaseModel):
    """Wrapper for user response."""
    user: User


import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.logger import get_logger






# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
logger = get_logger(__name__)



def get_password_hash(password: str) -> str:
    if isinstance(password, str):
        password = password.encode("utf-8")
    sha256_hash = hashlib.sha256(password).hexdigest()  # str, 64 chars
    return pwd_context.hash(sha256_hash)  # bcrypt sees 64 chars, safe


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password by applying SHA-256 (hex) + bcrypt."""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")
    sha256_hash = hashlib.sha256(plain_password).hexdigest()
    return pwd_context.verify(sha256_hash, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt
     



async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user from db using JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
        
    # Now you have user_id, you can get user from your database (just for example i am using supabase you can replace it)
    # Get user from our custom users table
    
    
    # user = supabase_auth.supabase.table("users").select("*").eq("id", user_id).execute()
    # if not user.data:
    #     raise credentials_exception
    
    
    return payload 

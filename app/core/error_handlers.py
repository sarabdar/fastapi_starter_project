"""
Centralized Error Handling
Provides consistent error responses across the application
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import logging

from app.core.logger import get_logger
logger = get_logger(__name__)


class AppException(Exception):
    """Base exception for application-specific errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(AppException):
    """Authorization/Permission related errors"""
    def __init__(self, message: str = "Insufficient permissions", details: dict = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class NotFoundError(AppException):
    """Resource not found errors"""
    def __init__(self, resource: str = "Resource", details: dict = None):
        message = f"{resource} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(AppException):
    """Data validation errors"""
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class ConflictError(AppException):
    """Resource conflict errors (e.g., duplicate email, duplicate key)"""
    def __init__(self, message: str = "Resource already exists", details: dict = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class DatabaseError(AppException):
    """Database operation errors"""
    def __init__(self, message: str = "Database operation failed", details: dict = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class FileUploadError(AppException):
    """File upload related errors"""
    def __init__(self, message: str = "File upload failed", details: dict = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


# Error response formatter
def format_error_response(
    status_code: int,
    message: str,
    details: dict = None,
    path: str = None
) -> dict:
    """Format error response consistently"""
    response = {
        "error": {
            "status_code": status_code,
            "message": message,
            "type": "error"
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if path:
        response["error"]["path"] = path
    
    return response


# Exception handlers for FastAPI
async def app_exception_handler(request: Request, exc: AppException):
    """Handler for custom application exceptions"""
    logger.error(
        f"AppException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log detailed validation errors to console
    error_details = "\n".join([
        f"  - Field '{err['field']}': {err['message']} (type: {err['type']})"
        for err in errors
    ])
    logger.warning(
        f"Validation error on {request.url.path}:\n{error_details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed",
            details={"validation_errors": errors},
            path=request.url.path
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for FastAPI HTTP exceptions"""
    logger.error(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            path=request.url.path
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for unexpected exceptions"""
    logger.exception(
        f"Unexpected error on {request.url.path}: {str(exc)}",
        exc_info=exc
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred. Please try again later.",
            details={"error_type": type(exc).__name__} if logger.level == logging.DEBUG else None,
            path=request.url.path
        )
    )

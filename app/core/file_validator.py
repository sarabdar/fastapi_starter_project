"""
File Upload Validator and Sanitizer
Prevents malicious file uploads and validates file types
"""

import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
import re

from app.core.error_handlers import FileUploadError

# Try to import magic libraries (platform-dependent)
try:
    import magic  # python-magic or python-magic-bin
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    
try:
    import filetype  # Pure Python alternative (Azure)
    FILETYPE_AVAILABLE = True
except ImportError:
    FILETYPE_AVAILABLE = False

if not MAGIC_AVAILABLE and not FILETYPE_AVAILABLE:
    raise ImportError(
        "No file type detection library available. "
        "Install 'python-magic-bin' (Windows) or 'filetype' (Azure/Linux)"
    )


class FileValidator:
    """Validates and sanitizes uploaded files"""
    
    # Allowed MIME types for images
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg", 
        "image/png",
        "image/webp",
        "image/gif"
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Dangerous file patterns to reject
    DANGEROUS_PATTERNS = [
        r"\.php",
        r"\.exe",
        r"\.sh",
        r"\.bat",
        r"\.cmd",
        r"\.com",
        r"\.pif",
        r"\.scr",
        r"\.vbs",
        r"\.js",
        r"\.jar",
        r"\.zip",
        r"\.rar",
        r"\.7z"
    ]
    
    @staticmethod
    async def validate_image(
        file: UploadFile,
        max_size: int = MAX_FILE_SIZE
    ) -> Tuple[bytes, str]:
        """
        Validate uploaded image file.
        
        Args:
            file: Uploaded file
            max_size: Maximum allowed file size in bytes
            
        Returns:
            Tuple of (file_content, content_type)
            
        Raises:
            FileUploadError: If validation fails
        """
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer
        await file.seek(0)
        
        # 1. Check file size
        if file_size == 0:
            raise FileUploadError("Empty file uploaded")
        
        if file_size > max_size:
            raise FileUploadError(
                f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB",
                details={"file_size": file_size, "max_size": max_size}
            )
        
        # 2. Validate filename
        if not file.filename:
            raise FileUploadError("Filename is required")
        
        # Check for dangerous patterns in filename
        for pattern in FileValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, file.filename, re.IGNORECASE):
                raise FileUploadError(
                    "Invalid file type detected",
                    details={"filename": file.filename}
                )
        
        # 3. Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise FileUploadError(
                f"Invalid file extension. Allowed: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}",
                details={"extension": file_ext}
            )
        
        # 4. Validate MIME type (checks actual file content, not just extension)
        mime = None
        
        # Try python-magic first (Windows with python-magic-bin)
        if MAGIC_AVAILABLE:
            try:
                mime = magic.from_buffer(content, mime=True)
            except Exception as e:
                # Fall through to filetype if magic fails
                pass
        
        # Try filetype as fallback (Azure/Linux or if magic failed)
        if mime is None and FILETYPE_AVAILABLE:
            try:
                kind = filetype.guess(content)
                mime = kind.mime if kind else None
            except Exception as e:
                pass
        
        # If we still don't have a MIME type, raise error
        if mime is None:
            raise FileUploadError(
                "Could not determine file type",
                details={"available_libraries": {
                    "magic": MAGIC_AVAILABLE,
                    "filetype": FILETYPE_AVAILABLE
                }}
            )
        
        if mime not in FileValidator.ALLOWED_IMAGE_TYPES:
            raise FileUploadError(
                f"Invalid file type. Detected: {mime}",
                details={"detected_type": mime, "allowed_types": list(FileValidator.ALLOWED_IMAGE_TYPES)}
            )
        
        # 5. Additional security: Check for embedded scripts in image metadata
        # This is a basic check - for production, consider using a library like PIL
        dangerous_strings = [b"<?php", b"<script", b"javascript:", b"eval("]
        for dangerous in dangerous_strings:
            if dangerous in content:
                raise FileUploadError(
                    "Potentially malicious content detected in file",
                    details={"reason": "embedded_script"}
                )
        
        return content, mime
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and other attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '_', filename)
        
        # Remove multiple dots (except for extension)
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            name = name.replace('.', '_')
            filename = f"{name}.{ext}"
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            filename = f"{name[:250]}.{ext}"
        
        return filename
    
    @staticmethod
    def generate_unique_filename(original_filename: str, content: bytes) -> str:
        """
        Generate a unique filename using hash of content.
        
        Args:
            original_filename: Original filename
            content: File content
            
        Returns:
            Unique filename
        """
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        
        # Generate hash from content
        file_hash = hashlib.sha256(content).hexdigest()[:16]
        
        # Create unique filename
        return f"{file_hash}{ext}"


# Dependency for FastAPI endpoints
async def validate_uploaded_image(file: UploadFile) -> Tuple[bytes, str, str]:
    """
    FastAPI dependency to validate uploaded images.
    
    Returns:
        Tuple of (content, mime_type, sanitized_filename)
    """
    validator = FileValidator()
    
    # Validate file
    content, mime_type = await validator.validate_image(file)
    
    # Sanitize and generate unique filename
    sanitized_name = validator.sanitize_filename(file.filename)
    unique_filename = validator.generate_unique_filename(sanitized_name, content)
    
    return content, mime_type, unique_filename

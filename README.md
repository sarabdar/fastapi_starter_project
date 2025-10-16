# FastAPI Starter Project

A production-ready FastAPI starter template with essential features and best practices for building robust web applications.

## 🚀 Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (RBAC)
  - Secure password hashing
  - Token refresh mechanism

- **API Features**
  - Request validation with Pydantic
  - Rate limiting
  - Custom error handling
  - API versioning
  - CORS support

- **Database**
  - SQLAlchemy ORM integration
  - Database migrations with Alembic (coming soon)
  - Connection pooling
  - Base model with common fields

- **Background Tasks & Scheduling**
  - Built-in cron job scheduler
  - Example jobs for common tasks
  - Async task support

- **Security**
  - Environment-based configuration
  - Secure password hashing
  - CORS middleware
  - Rate limiting
  - Request validation
  - **File Upload Security**
    - MIME type validation
    - File size restrictions
    - File extension whitelisting
    - Malware scanning (via magic numbers)
    - Safe filename generation
    - Content type verification
  - **Permission System**
    - Role-based access control (RBAC)
    - Resource ownership verification
    - Fine-grained permission checks
    - Custom permission decorators
    - Audit logging for security events

- **Development Tools**
  - Structured logging
  - Request ID tracking
  - API documentation (Swagger UI & ReDoc)
  - Development/Production configuration

## 🛠️ Project Structure

```
fastapi_project_starter/
├── app/
│   ├── api/                # API routes
│   ├── core/               # Core functionality
│   │   ├── config.py       # Application configuration
│   │   ├── security.py     # Authentication and security
│   │   ├── permissions.py  # Permission classes
│   │   └── error_handlers.py # Custom error handlers
│   ├── cron_jobs/          # Scheduled jobs
│   ├── db/                 # Database models and session
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── .env.example            # Example environment variables
└── requirements.txt        # Project dependencies
```

## 🔒 File Upload Validation

The project includes a robust file validation system to securely handle file uploads. Here's how to use it:

```python
from fastapi import UploadFile, Depends
from app.core.file_validator import validate_uploaded_image

@app.post("/upload")
async def upload_file(file: UploadFile):
    # This validates the file and returns (content, mime_type, safe_filename)
    content, mime_type, filename = await validate_uploaded_image(file)
    
    # Process the validated file...
    return {"filename": filename, "size": len(content), "type": mime_type}
```

### Validation Features:
- **Type Checking**: Validates file MIME types and extensions
- **Size Limits**: Configurable maximum file size
- **Security**: Detects and blocks potentially malicious files
- **Sanitization**: Cleans filenames to prevent path traversal

## 🔐 Permission System

The project includes a flexible permission system for controlling access to resources:

```python
from app.core.permissions import check_role, check_ownership, check_role_or_ownership

# Check if user has admin role
check_role(current_user, ["admin"])

# Check if user owns the resource
check_ownership(current_user, resource_owner_id, "resource")

# Check role OR ownership (admin can access all, users only their own)
check_role_or_ownership(current_user, ["admin"], resource_owner_id, "access resource")
```

### Permission Features:
- **Role-based Access Control (RBAC)**: Define roles and their permissions
- **Ownership Verification**: Ensure users can only access their own resources
- **Flexible Checks**: Support for both role and ownership checks
- **Detailed Error Messages**: Clear error messages for debugging

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastapi-starter.git
   cd fastapi-starter
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Update the .env file with your configuration
   ```

3. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔒 Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer your_jwt_token_here
```

### Example Login Request

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'
```

## 🕒 Scheduled Jobs

The project includes example scheduled jobs in `app/cron_jobs/`:

- `cleanup_old_data()` - Cleans up old or expired data
- `generate_daily_reports()` - Generates daily reports
- `backup_critical_data()` - Backs up important data
- `send_daily_notifications()` - Sends scheduled notifications


## 🛡️ Security Best Practices

- Never commit sensitive data to version control
- Use environment variables for configuration
- Enable CORS only for trusted origins
- Implement rate limiting on public endpoints
- Use HTTPS in production
- Keep dependencies up to date


Built with ❤️ for developers who love clean, maintainable code.

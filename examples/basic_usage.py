"""Basic usage example with custom JWT provider."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_swagger_auth import SwaggerAuthDev

# Create FastAPI app
app = FastAPI(title="Basic Usage Example", debug=True)

# Add CORS middleware (recommended for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Swagger auto-authentication
SwaggerAuthDev(
    app,
    auth_provider="custom",
    dev_credentials={
        "email": "admin@dev.local",
        "sub": "user_123",
        "role": "admin",
    },
)

# Security scheme for endpoints
security = HTTPBearer()


@app.get("/")
async def root():
    """Public endpoint."""
    return {"message": "Hello World"}


@app.get("/protected")
async def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Protected endpoint requiring authentication."""
    return {
        "message": "This is a protected endpoint",
        "token": credentials.credentials[:20] + "...",
    }


@app.get("/admin")
async def admin_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Admin-only endpoint."""
    return {
        "message": "Admin access granted",
        "token": credentials.credentials[:20] + "...",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

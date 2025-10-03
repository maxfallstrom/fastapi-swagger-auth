"""Supabase authentication example."""

import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_swagger_auth import SwaggerAuthDev

# Create FastAPI app
app = FastAPI(title="Supabase Example", debug=True)

# Add CORS middleware (recommended for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Swagger auto-authentication with Supabase
# Make sure to set SUPABASE_URL and SUPABASE_KEY environment variables
SwaggerAuthDev(
    app,
    auth_provider="supabase",
    dev_credentials={
        "email": os.getenv("DEV_EMAIL", "admin@dev.local"),
        "password": os.getenv("DEV_PASSWORD", "devpass123"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_KEY"),
    },
)

security = HTTPBearer()


@app.get("/")
async def root():
    """Public endpoint."""
    return {"message": "Supabase Auth Example"}


@app.get("/user/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user profile (requires authentication)."""
    return {
        "message": "User profile endpoint",
        "authenticated": True,
        "token_preview": credentials.credentials[:30] + "...",
    }


@app.post("/data")
async def create_data(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create data (requires authentication)."""
    return {
        "message": "Data created successfully",
        "authenticated": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

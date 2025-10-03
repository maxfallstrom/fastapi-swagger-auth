"""Custom provider implementation example."""

from typing import Any, Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_swagger_auth import SwaggerAuthDev
from fastapi_swagger_auth.providers.base import AuthProvider
from fastapi_swagger_auth.providers.custom import CustomJWTProvider


class MyCustomProvider(AuthProvider):
    """Example custom provider with custom logic."""

    def __init__(self):
        # Could integrate with your own auth service
        self.jwt_provider = CustomJWTProvider(
            secret_key="my-custom-secret-key",
            expiry_minutes=30,
        )

    async def get_token(self, credentials: Dict[str, Any]) -> str:
        """Authenticate and get token.

        In a real implementation, you might:
        - Call your own auth API
        - Validate credentials against database
        - Integrate with third-party auth service
        """
        email = credentials.get("email")
        password = credentials.get("password")

        # Example: Simple validation (DON'T USE IN PRODUCTION!)
        if email == "admin@example.com" and password == "secret":
            return await self.jwt_provider.get_token(
                {"email": email, "sub": "admin_user", "role": "admin"}
            )
        else:
            raise Exception("Invalid credentials")

    async def refresh_token(self, current_token: str) -> str:
        """Refresh the token."""
        return await self.jwt_provider.refresh_token(current_token)

    def get_token_expiry(self, token: str) -> int:
        """Get token expiry."""
        return self.jwt_provider.get_token_expiry(token)


# Create FastAPI app
app = FastAPI(title="Custom Provider Example", debug=True)

# Add CORS middleware (recommended for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use custom provider instance
SwaggerAuthDev(
    app,
    provider_instance=MyCustomProvider(),
    dev_credentials={
        "email": "admin@example.com",
        "password": "secret",
    },
)

security = HTTPBearer()


@app.get("/")
async def root():
    """Public endpoint."""
    return {"message": "Custom Provider Example"}


@app.get("/protected")
async def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Protected endpoint."""
    return {
        "message": "Authenticated with custom provider",
        "token_preview": credentials.credentials[:30] + "...",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

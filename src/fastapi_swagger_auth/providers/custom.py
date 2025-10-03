"""Custom JWT provider for simple token generation."""

import time
from typing import Any, Dict

from jose import jwt

from fastapi_swagger_auth.providers.base import AuthProvider


class CustomJWTProvider(AuthProvider):
    """Simple JWT provider for development/testing.

    Generates JWT tokens without external authentication service.
    Useful for testing or when you have your own auth logic.
    """

    def __init__(
        self,
        secret_key: str = "dev-secret-key-change-in-production",
        algorithm: str = "HS256",
        expiry_minutes: int = 60,
    ):
        """Initialize custom JWT provider.

        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm (default: HS256)
            expiry_minutes: Token expiry time in minutes (default: 60)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiry_minutes = expiry_minutes

    async def get_token(self, credentials: Dict[str, Any]) -> str:
        """Generate a JWT token with provided credentials.

        Args:
            credentials: Dictionary with user info to embed in token
                        (e.g., {"email": "user@example.com", "sub": "user_id"})

        Returns:
            JWT token string
        """
        # Create payload with expiry
        payload = {
            **credentials,
            "exp": int(time.time()) + (self.expiry_minutes * 60),
            "iat": int(time.time()),
        }

        # Generate token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    async def refresh_token(self, current_token: str) -> str:
        """Refresh existing token.

        Args:
            current_token: Current JWT token

        Returns:
            New JWT token with extended expiry

        Raises:
            Exception: If token is invalid
        """
        # Decode current token (without verification for dev purposes)
        claims = jwt.get_unverified_claims(current_token)

        # Remove exp and iat for refresh
        claims.pop("exp", None)
        claims.pop("iat", None)

        # Generate new token with same claims
        return await self.get_token(claims)

    def get_token_expiry(self, token: str) -> int:
        """Get token expiration time in seconds.

        Args:
            token: JWT token to parse

        Returns:
            Number of seconds until token expires
        """
        try:
            claims = jwt.get_unverified_claims(token)
            exp = claims.get("exp")
            if exp:
                return max(int(exp - time.time()), 0)
        except Exception:
            pass
        return 0

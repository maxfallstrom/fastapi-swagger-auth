"""Supabase authentication provider."""

import os
from typing import Any, Dict, Optional

import httpx
from jose import jwt

from fastapi_swagger_auth.providers.base import AuthProvider


class SupabaseProvider(AuthProvider):
    """Supabase authentication provider.

    Authenticates with Supabase Auth and retrieves JWT tokens.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        """Initialize Supabase provider.

        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase anon/service key (or set SUPABASE_KEY env var)

        Raises:
            ValueError: If URL or key not provided
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")

        if not self.supabase_url:
            raise ValueError(
                "supabase_url required. Provide in constructor or set SUPABASE_URL env var"
            )
        if not self.supabase_key:
            raise ValueError(
                "supabase_key required. Provide in constructor or set SUPABASE_KEY env var"
            )

        # Remove trailing slash from URL
        self.supabase_url = self.supabase_url.rstrip("/")
        self.auth_url = f"{self.supabase_url}/auth/v1"

    async def get_token(self, credentials: Dict[str, Any]) -> str:
        """Get authentication token from Supabase.

        Args:
            credentials: Dictionary with "email" and "password" keys

        Returns:
            JWT access token

        Raises:
            ValueError: If credentials missing required fields
            Exception: If authentication fails
        """
        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            raise ValueError("credentials must contain 'email' and 'password'")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token?grant_type=password",
                json={"email": email, "password": password},
                headers={
                    "apikey": self.supabase_key,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                error_msg = response.json().get("error_description", response.text)
                raise Exception(f"Supabase auth failed: {error_msg}")

            data = response.json()
            return data["access_token"]

    async def refresh_token(self, current_token: str) -> str:
        """Refresh Supabase token.

        Args:
            current_token: Current JWT token (not used, requires refresh_token)

        Returns:
            New JWT token

        Raises:
            NotImplementedError: Refresh requires refresh_token from login response
        """
        raise NotImplementedError(
            "Token refresh requires storing refresh_token from initial login. "
            "Consider re-authenticating instead."
        )

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
                import time

                return max(int(exp - time.time()), 0)
        except Exception:
            pass
        return 0

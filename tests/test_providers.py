"""Tests for authentication providers."""

import time

import pytest
from jose import jwt

from fastapi_swagger_auth.providers.custom import CustomJWTProvider


@pytest.mark.asyncio
async def test_custom_jwt_provider_get_token():
    """Test custom JWT provider token generation."""
    provider = CustomJWTProvider(secret_key="test-secret", expiry_minutes=60)

    token = await provider.get_token({"email": "test@example.com", "sub": "user_123"})

    # Verify token is valid
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify claims
    claims = jwt.get_unverified_claims(token)
    assert claims["email"] == "test@example.com"
    assert claims["sub"] == "user_123"
    assert "exp" in claims
    assert "iat" in claims


@pytest.mark.asyncio
async def test_custom_jwt_provider_token_expiry():
    """Test token expiry calculation."""
    provider = CustomJWTProvider(secret_key="test-secret", expiry_minutes=60)

    token = await provider.get_token({"email": "test@example.com"})
    expiry_seconds = provider.get_token_expiry(token)

    # Should be approximately 60 minutes (3600 seconds)
    assert 3590 < expiry_seconds <= 3600


@pytest.mark.asyncio
async def test_custom_jwt_provider_refresh_token():
    """Test token refresh functionality."""
    provider = CustomJWTProvider(secret_key="test-secret", expiry_minutes=30)

    # Get initial token
    original_token = await provider.get_token({"email": "test@example.com", "sub": "user_123"})

    # Wait a moment
    time.sleep(1)

    # Refresh token
    new_token = await provider.refresh_token(original_token)

    # Tokens should be different (different exp/iat)
    assert original_token != new_token

    # But should have same claims
    original_claims = jwt.get_unverified_claims(original_token)
    new_claims = jwt.get_unverified_claims(new_token)

    assert original_claims["email"] == new_claims["email"]
    assert original_claims["sub"] == new_claims["sub"]
    # New token should have later expiry
    assert new_claims["exp"] > original_claims["exp"]


@pytest.mark.asyncio
async def test_custom_jwt_provider_custom_algorithm():
    """Test using custom JWT algorithm."""
    provider = CustomJWTProvider(secret_key="test-secret", algorithm="HS512")

    token = await provider.get_token({"email": "test@example.com"})
    claims = jwt.get_unverified_claims(token)

    assert claims["email"] == "test@example.com"

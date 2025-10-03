"""Tests for core SwaggerAuthDev functionality."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_swagger_auth import SwaggerAuthDev
from fastapi_swagger_auth.providers.custom import CustomJWTProvider


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    app = FastAPI(title="Test App", debug=True)

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    return app


def test_swagger_auth_disabled_in_non_debug_mode():
    """Test that SwaggerAuthDev is disabled when debug=False."""
    app = FastAPI(debug=False)
    SwaggerAuthDev(app, auth_provider="custom", dev_credentials={"email": "test@example.com"})

    client = TestClient(app)
    # Should get standard Swagger UI since auth is disabled
    response = client.get("/docs")
    assert response.status_code == 200


def test_swagger_auth_enabled_in_debug_mode(app):
    """Test that SwaggerAuthDev is enabled in debug mode."""
    SwaggerAuthDev(app, auth_provider="custom", dev_credentials={"email": "test@example.com"})

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"FastAPI-Swagger-Auth" in response.content


def test_swagger_auth_with_custom_token_getter(app):
    """Test using a custom token getter function."""

    def get_test_token():
        return "test-token-12345"

    SwaggerAuthDev(app, token_getter=get_test_token)

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"test-token-12345" in response.content


def test_swagger_auth_with_provider_instance(app):
    """Test using a custom provider instance."""
    provider = CustomJWTProvider(secret_key="test-secret")
    SwaggerAuthDev(
        app, provider_instance=provider, dev_credentials={"email": "test@example.com", "sub": "123"}
    )

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"FastAPI-Swagger-Auth" in response.content


def test_swagger_auth_explicit_enable():
    """Test explicitly enabling SwaggerAuthDev even in non-debug mode."""
    app = FastAPI(debug=False)
    SwaggerAuthDev(
        app, enabled=True, auth_provider="custom", dev_credentials={"email": "test@example.com"}
    )

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_swagger_auth_explicit_disable(app):
    """Test explicitly disabling SwaggerAuthDev even in debug mode."""
    SwaggerAuthDev(
        app, enabled=False, auth_provider="custom", dev_credentials={"email": "test@example.com"}
    )

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    # Should get standard Swagger UI

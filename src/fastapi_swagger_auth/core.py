"""Core SwaggerAuthDev class for FastAPI integration."""

import logging
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jose import jwt

from fastapi_swagger_auth.config import SwaggerAuthConfig
from fastapi_swagger_auth.providers.base import AuthProvider
from fastapi_swagger_auth.swagger_ui import create_swagger_ui_html

logger = logging.getLogger(__name__)


class SwaggerAuthDev:
    """Automatic Swagger UI authentication for FastAPI development."""

    def __init__(
        self,
        app: FastAPI,
        auth_provider: str = "custom",
        dev_credentials: Optional[Dict[str, Any]] = None,
        token_getter: Optional[Callable[[], str]] = None,
        auto_refresh: bool = True,
        enabled: Optional[bool] = None,
        provider_instance: Optional[AuthProvider] = None,
    ):
        """Initialize Swagger authentication.

        Args:
            app: FastAPI application instance
            auth_provider: Provider name ("custom", "supabase", "auth0", "firebase")
            dev_credentials: Credentials dict (e.g., {"email": "...", "password": "..."})
            token_getter: Optional custom function to get token (overrides provider)
            auto_refresh: Enable automatic token refresh
            enabled: Explicitly enable/disable (None = auto-detect from debug mode)
            provider_instance: Optional pre-configured AuthProvider instance
        """
        self.app = app
        self.config = SwaggerAuthConfig(
            auth_provider=auth_provider,
            dev_credentials=dev_credentials,
            auto_refresh=auto_refresh,
            enabled=enabled,
        )
        self.token_getter = token_getter
        self.provider_instance = provider_instance
        self._token: Optional[str] = None

        # Check if should be enabled
        if not self.config.is_enabled(app.debug):
            logger.info(
                "[FastAPI-Swagger-Auth] Disabled (not in debug mode). "
                "Set enabled=True to force enable."
            )
            return

        # Override Swagger UI endpoint
        self._override_swagger_ui()
        logger.info(
            "[FastAPI-Swagger-Auth] Enabled - Swagger UI will auto-authenticate"
        )

    async def _get_token(self) -> str:
        """Get authentication token from configured source.

        Returns:
            JWT token string

        Raises:
            ValueError: If no token source is configured
        """
        # Use custom token getter if provided
        if self.token_getter:
            token = self.token_getter()
            logger.debug("[FastAPI-Swagger-Auth] Token obtained from custom getter")
            return token

        # Use provider instance if provided
        if self.provider_instance:
            if not self.config.dev_credentials:
                raise ValueError("dev_credentials required when using provider")
            token = await self.provider_instance.get_token(self.config.dev_credentials)
            logger.debug(
                f"[FastAPI-Swagger-Auth] Token obtained from {self.config.auth_provider} provider"
            )
            return token

        # Lazy import providers to get token
        if self.config.auth_provider == "custom":
            from fastapi_swagger_auth.providers.custom import CustomJWTProvider

            if not self.config.dev_credentials:
                raise ValueError("dev_credentials required for custom provider")
            provider = CustomJWTProvider()
            token = await provider.get_token(self.config.dev_credentials)
        elif self.config.auth_provider == "supabase":
            from fastapi_swagger_auth.providers.supabase import SupabaseProvider

            if not self.config.dev_credentials:
                raise ValueError("dev_credentials required for Supabase provider")
            # Supabase requires URL and key from environment or credentials
            provider = SupabaseProvider(
                supabase_url=self.config.dev_credentials.get("supabase_url"),
                supabase_key=self.config.dev_credentials.get("supabase_key"),
            )
            token = await provider.get_token(self.config.dev_credentials)
        else:
            raise ValueError(
                f"Unsupported auth_provider: {self.config.auth_provider}. "
                "Use 'custom', 'supabase', or provide a provider_instance."
            )

        logger.debug(
            f"[FastAPI-Swagger-Auth] Token obtained from {self.config.auth_provider} provider"
        )
        return token

    def _get_token_expiry(self, token: str) -> int:
        """Get token expiry time in seconds.

        Args:
            token: JWT token

        Returns:
            Seconds until expiry, or 3600 if cannot parse
        """
        try:
            claims = jwt.get_unverified_claims(token)
            exp = claims.get("exp")
            if exp:
                import time

                return max(int(exp - time.time()), 0)
        except Exception as e:
            logger.warning(f"[FastAPI-Swagger-Auth] Could not parse token expiry: {e}")
        return 3600  # Default to 1 hour

    def _override_swagger_ui(self):
        """Override the default Swagger UI endpoint with authenticated version."""

        # Remove existing /docs route if it exists
        routes_to_remove = []
        for route in self.app.routes:
            if hasattr(route, "path") and route.path == self.config.swagger_ui_path:
                routes_to_remove.append(route)

        for route in routes_to_remove:
            self.app.routes.remove(route)

        @self.app.get(self.config.swagger_ui_path, include_in_schema=False)
        async def custom_swagger_ui_html():
            """Custom Swagger UI with auto-authentication."""
            try:
                # Get token
                token = await self._get_token()
                token_expiry = self._get_token_expiry(token)

                # Generate custom Swagger UI HTML
                html_content = create_swagger_ui_html(
                    openapi_url=self.config.openapi_url,
                    title=self.app.title + " - API Docs",
                    token=token,
                    auto_refresh=self.config.auto_refresh,
                    token_expiry_seconds=token_expiry,
                )

                return HTMLResponse(content=html_content)

            except Exception as e:
                logger.error(f"[FastAPI-Swagger-Auth] Failed to get token: {e}")
                # Fallback to standard docs with error message
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Authentication Error</title></head>
                <body>
                    <h1>FastAPI Swagger Auth - Error</h1>
                    <p>Failed to authenticate: {str(e)}</p>
                    <p>Please check your dev_credentials configuration.</p>
                    <a href="{self.config.openapi_url}">View OpenAPI Schema</a>
                </body>
                </html>
                """
                return HTMLResponse(content=error_html, status_code=500)

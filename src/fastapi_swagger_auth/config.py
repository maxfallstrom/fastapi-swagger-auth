"""Configuration and settings for FastAPI Swagger Auth."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SwaggerAuthConfig:
    """Configuration for Swagger authentication."""

    auth_provider: str = "custom"
    dev_credentials: Optional[dict] = None
    auto_refresh: bool = True
    enabled: Optional[bool] = None  # None = auto-detect from debug mode
    swagger_ui_path: str = "/docs"
    openapi_url: str = "/openapi.json"

    def is_enabled(self, debug_mode: bool) -> bool:
        """Check if Swagger auth should be enabled.

        Args:
            debug_mode: Whether FastAPI is in debug mode

        Returns:
            True if should be enabled, False otherwise
        """
        if self.enabled is not None:
            return self.enabled
        # Auto-detect: only enable in debug mode
        return debug_mode

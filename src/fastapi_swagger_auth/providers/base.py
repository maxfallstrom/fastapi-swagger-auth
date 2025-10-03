"""Base authentication provider interface."""

from abc import ABC, abstractmethod


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""

    @abstractmethod
    async def get_token(self, credentials: dict) -> str:
        """Get authentication token from provider.

        Args:
            credentials: Dictionary containing authentication credentials
                        (e.g., {"email": "user@example.com", "password": "pass"})

        Returns:
            JWT token string

        Raises:
            Exception: If authentication fails
        """
        pass

    @abstractmethod
    async def refresh_token(self, current_token: str) -> str:
        """Refresh existing token if supported.

        Args:
            current_token: Current JWT token to refresh

        Returns:
            New JWT token string

        Raises:
            NotImplementedError: If provider doesn't support token refresh
        """
        pass

    @abstractmethod
    def get_token_expiry(self, token: str) -> int:
        """Get token expiration time in seconds.

        Args:
            token: JWT token to parse

        Returns:
            Number of seconds until token expires
        """
        pass

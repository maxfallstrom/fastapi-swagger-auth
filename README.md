# FastAPI Swagger Auth

Automatically authenticate Swagger UI in FastAPI during development - solving the pain of manually copying JWT tokens every time you want to test endpoints.

## Features

- **Automatic Authentication** - Swagger UI auto-injects JWT tokens
- **Zero Configuration** - Works out of the box with sensible defaults
- **Multiple Providers** - Supabase or custom JWT (extensible for any auth service)
- **Security-First** - Only activates in development mode
- **Auto-Refresh** - Tokens refresh automatically before expiry
- **Type-Safe** - Full type hints for better IDE support

## Installation

```bash
pip install fastapi-swagger-auth
```

With Supabase support:

```bash
pip install fastapi-swagger-auth[supabase]
```

## Quick Start

### Basic Usage (Custom JWT)

```python
from fastapi import FastAPI
from fastapi_swagger_auth import SwaggerAuthDev

app = FastAPI(debug=True)

# One-line setup
SwaggerAuthDev(
    app,
    auth_provider="custom",
    dev_credentials={
        "email": "admin@dev.local",
        "sub": "user_123",
    }
)
```

### Supabase Provider

```python
SwaggerAuthDev(
    app,
    auth_provider="supabase",
    dev_credentials={
        "email": "admin@dev.local",
        "password": "devpass123",
        "supabase_url": "https://your-project.supabase.co",
        "supabase_key": "your-anon-key",
    }
)
```

### Custom Token Getter

```python
def get_my_token():
    # Your custom logic to get a token
    return "my-jwt-token"

SwaggerAuthDev(app, token_getter=get_my_token)
```

### Custom Provider

```python
from fastapi_swagger_auth.providers.base import AuthProvider

class MyProvider(AuthProvider):
    async def get_token(self, credentials: dict) -> str:
        # Your auth logic
        return "jwt-token"

    async def refresh_token(self, current_token: str) -> str:
        # Your refresh logic
        return "new-jwt-token"

    def get_token_expiry(self, token: str) -> int:
        # Parse token and return seconds until expiry
        return 3600

SwaggerAuthDev(
    app,
    provider_instance=MyProvider(),
    dev_credentials={"email": "admin@dev.local", "password": "secret"}
)
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `FastAPI` | Required | FastAPI application instance |
| `auth_provider` | `str` | `"custom"` | Provider type: "custom" or "supabase" |
| `dev_credentials` | `dict` | `None` | Credentials for authentication |
| `token_getter` | `callable` | `None` | Custom function to get token (overrides provider) |
| `auto_refresh` | `bool` | `True` | Enable automatic token refresh |
| `enabled` | `bool` | `None` | Explicitly enable/disable (None = auto-detect from debug mode) |
| `provider_instance` | `AuthProvider` | `None` | Custom provider instance |

## How It Works

1. **Initialization** - SwaggerAuthDev validates environment (dev mode only by default)
2. **Authentication** - Selected provider authenticates using `dev_credentials`
3. **Token Injection** - Custom Swagger UI HTML injects JWT via `requestInterceptor`
4. **Auto-Refresh** - Token automatically refreshes before expiry (optional)

## Security

- **Development Only** - Only activates when `app.debug=True` by default
- **No Production Risk** - Explicitly enable with `enabled=True` if needed
- **Clear Logging** - Debug messages show authentication status
- **Graceful Fallback** - Shows instructions if authentication fails

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py` - Simple custom JWT provider
- `supabase_example.py` - Supabase authentication
- `custom_provider.py` - Custom provider implementation

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```


**FastAPI Swagger Auth** eliminates this workflow entirely. Similar to Swashbuckle in .NET, it's a development tool that just works.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

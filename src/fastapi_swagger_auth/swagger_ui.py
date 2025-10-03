"""Custom Swagger UI HTML generation with auto-authentication."""


def create_swagger_ui_html(
    openapi_url: str,
    title: str,
    token: str,
    auto_refresh: bool = True,
    token_expiry_seconds: int = 3600,
) -> str:
    """Generate custom Swagger UI HTML with auto-authentication.

    Args:
        openapi_url: URL to the OpenAPI schema
        title: Page title
        token: JWT token to inject
        auto_refresh: Whether to auto-refresh token before expiry
        token_expiry_seconds: Token expiry time in seconds (for refresh scheduling)

    Returns:
        HTML string for custom Swagger UI
    """
    refresh_script = ""
    if auto_refresh and token_expiry_seconds > 0:
        # Refresh 5 minutes before expiry
        refresh_delay_ms = max((token_expiry_seconds - 300) * 1000, 60000)
        refresh_script = f"""
        // Auto-refresh token before expiry
        setTimeout(() => {{
            console.log('[FastAPI-Swagger-Auth] Token expiring soon, refreshing page...');
            window.location.reload();
        }}, {refresh_delay_ms});
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <link rel="icon" type="image/png" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        .swagger-ui .topbar {{
            background-color: #1f8954;
        }}
        .swagger-ui .info .title small {{
            background-color: #ffc107;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 10px;
            font-size: 12px;
            color: #000;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: 'StandaloneLayout',
                requestInterceptor: (req) => {{
                    req.headers['Authorization'] = 'Bearer {token}';
                    console.log('[FastAPI-Swagger-Auth] Auto-injecting Bearer token');
                    return req;
                }},
                onComplete: function() {{
                    // Auto-authorize the Swagger UI with the token
                    ui.preauthorizeApiKey('HTTPBearer', '{token}');
                    console.log('[FastAPI-Swagger-Auth] Swagger UI initialized');
                    console.log('[FastAPI-Swagger-Auth] Development mode active');
                    console.log('[FastAPI-Swagger-Auth] Token auto-populated');
                    {refresh_script}
                }}
            }});

            window.ui = ui;
        }};
    </script>
</body>
</html>"""

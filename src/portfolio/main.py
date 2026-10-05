from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from portfolio.config import Settings, get_settings
from portfolio.routes import meta


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    docs_enabled = not settings.is_production

    app = FastAPI(
        title="Portfolio",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.include_router(meta.router)
    return app


app = create_app()

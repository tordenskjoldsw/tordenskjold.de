import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from portfolio.config import Settings, get_settings
from portfolio.middleware import SecurityHeadersMiddleware
from portfolio.routes import devlog, meta, pages
from portfolio.routes.errors import register_error_handlers
from portfolio.services.content import load_content
from portfolio.static_files import STATIC_URL_PREFIX, CachedStaticFiles
from portfolio.templating import STATIC_DIR

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    docs_enabled = not settings.is_production

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        content = await asyncio.to_thread(
            load_content, settings.content_dir, STATIC_DIR
        )
        logger.info(
            "Loaded %d projects, %d devlog entries and %d certifications",
            len(content.projects),
            len(content.devlog),
            len(content.certifications),
        )
        app.state.content = content
        yield

    app = FastAPI(
        title="Portfolio",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    # Added last so it wraps everything, including host rejections.
    app.add_middleware(SecurityHeadersMiddleware)
    app.mount(STATIC_URL_PREFIX, CachedStaticFiles(directory=STATIC_DIR), name="static")
    register_error_handlers(app)
    app.include_router(meta.router)
    app.include_router(pages.router)
    app.include_router(devlog.router)
    return app


app = create_app()

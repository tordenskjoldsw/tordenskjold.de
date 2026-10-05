import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from portfolio.config import Settings, get_settings
from portfolio.routes import meta, pages
from portfolio.services.content import load_content
from portfolio.templating import STATIC_DIR, STATIC_URL_PREFIX

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    docs_enabled = not settings.is_production

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        content = await asyncio.to_thread(load_content, settings.content_dir)
        logger.info(
            "Loaded %d projects and %d certifications",
            len(content.projects),
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
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.mount(STATIC_URL_PREFIX, StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(meta.router)
    app.include_router(pages.router)
    return app


app = create_app()

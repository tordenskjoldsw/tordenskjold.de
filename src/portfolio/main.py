import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from portfolio.config import Settings, get_settings
from portfolio.middleware import SecurityHeadersMiddleware
from portfolio.models import Project
from portfolio.routes import devlog, meta, pages
from portfolio.routes.errors import register_error_handlers
from portfolio.services.content import load_content
from portfolio.services.github import RepoStatsCache, create_client, refresh_forever
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
        app.state.repo_stats = RepoStatsCache()
        if not settings.github_enabled:
            yield
            return
        async with github_refresh(settings, app.state.repo_stats, content.projects):
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


@asynccontextmanager
async def github_refresh(
    settings: Settings, cache: RepoStatsCache, projects: tuple[Project, ...]
) -> AsyncIterator[None]:
    # Runs in the background so a slow or unreachable GitHub never delays
    # startup or a request.
    async with create_client(
        settings.github_token, settings.github_timeout_seconds
    ) as client:
        task = asyncio.create_task(
            refresh_forever(cache, client, projects, settings.github_refresh_seconds)
        )
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


app = create_app()

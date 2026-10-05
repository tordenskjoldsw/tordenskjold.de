from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse, Response

from portfolio.config import Settings, get_app_settings
from portfolio.models import SiteContent
from portfolio.services.content import get_site_content
from portfolio.services.sitemap import sitemap_entries
from portfolio.templating import templates

SITEMAP_MEDIA_TYPE = "application/xml"

router = APIRouter(include_in_schema=False)


# FastAPI does not add HEAD to GET routes on its own, and uptime checks use it.
@router.api_route("/health", methods=["GET", "HEAD"], response_class=PlainTextResponse)
async def health() -> str:
    return "ok"


@router.api_route(
    "/robots.txt", methods=["GET", "HEAD"], response_class=PlainTextResponse
)
async def robots(settings: Annotated[Settings, Depends(get_app_settings)]) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {settings.base_url}/sitemap.xml\n"


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap(
    request: Request, content: Annotated[SiteContent, Depends(get_site_content)]
) -> Response:
    return templates.TemplateResponse(
        request,
        "sitemap.xml",
        {"entries": sitemap_entries(content)},
        media_type=SITEMAP_MEDIA_TYPE,
    )

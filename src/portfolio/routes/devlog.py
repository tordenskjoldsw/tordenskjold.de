from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from portfolio.config import Settings, get_app_settings
from portfolio.models import SiteContent
from portfolio.services.content import get_site_content
from portfolio.templating import templates

ATOM_MEDIA_TYPE = "application/atom+xml"

router = APIRouter(include_in_schema=False)
Content = Annotated[SiteContent, Depends(get_site_content)]


@router.api_route("/devlog", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def devlog_index(request: Request, content: Content) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "pages/devlog_index.html", {"entries": content.devlog}
    )


@router.api_route(
    "/devlog/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse
)
async def devlog_entry(request: Request, slug: str, content: Content) -> HTMLResponse:
    entry = content.devlog_entry(slug)
    if entry is None:
        raise HTTPException(status_code=404)
    project = content.project(entry.project) if entry.project else None
    return templates.TemplateResponse(
        request, "pages/devlog_entry.html", {"entry": entry, "project": project}
    )


@router.api_route("/feed.xml", methods=["GET", "HEAD"])
async def feed(
    request: Request,
    content: Content,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> Response:
    # Atom requires a feed-level "updated" date, and an empty devlog has no
    # honest one to give.
    if not content.devlog:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "feed.xml",
        {
            "entries": content.devlog,
            "updated": content.devlog[0].date,
            "base_url": settings.base_url,
        },
        media_type=ATOM_MEDIA_TYPE,
    )

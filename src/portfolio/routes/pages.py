from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from portfolio.models import SiteContent
from portfolio.services.content import get_site_content
from portfolio.templating import templates

LATEST_DEVLOG_COUNT = 3

router = APIRouter(include_in_schema=False)
Content = Annotated[SiteContent, Depends(get_site_content)]


@router.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(request: Request, content: Content) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {
            "projects": content.projects,
            "latest_devlog": content.devlog[:LATEST_DEVLOG_COUNT],
            "certifications": content.certifications,
        },
    )


@router.api_route(
    "/projects/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse
)
async def project_detail(request: Request, slug: str, content: Content) -> HTMLResponse:
    project = content.project(slug)
    if project is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "pages/project.html",
        {"project": project, "devlog": content.devlog_for(project)},
    )

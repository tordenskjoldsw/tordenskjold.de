from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from portfolio.models import SiteContent
from portfolio.services.content import get_site_content
from portfolio.templating import templates

router = APIRouter(include_in_schema=False)


@router.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(
    request: Request,
    content: Annotated[SiteContent, Depends(get_site_content)],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {
            "projects": content.projects,
            "certifications": content.certifications,
        },
    )

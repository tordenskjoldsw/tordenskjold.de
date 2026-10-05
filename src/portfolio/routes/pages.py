from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from portfolio.models import SiteContent
from portfolio.services.content import get_site_content
from portfolio.services.github import RepoStatsCache, get_repo_stats
from portfolio.templating import templates

LATEST_DEVLOG_COUNT = 3
# Keeps the home page short as projects are added; /projects lists all.
HOME_PROJECT_LIMIT = 4

router = APIRouter(include_in_schema=False)
Content = Annotated[SiteContent, Depends(get_site_content)]
StatsCache = Annotated[RepoStatsCache, Depends(get_repo_stats)]


@router.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(
    request: Request, content: Content, repo_stats: StatsCache
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/home.html",
        {
            "projects": content.projects[:HOME_PROJECT_LIMIT],
            "has_more_projects": len(content.projects) > HOME_PROJECT_LIMIT,
            "repo_stats": repo_stats.snapshot(),
            "latest_devlog": content.devlog[:LATEST_DEVLOG_COUNT],
            "certifications": content.certifications,
        },
    )


@router.api_route("/projects", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def projects(
    request: Request, content: Content, repo_stats: StatsCache
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/projects.html",
        {"projects": content.projects, "repo_stats": repo_stats.snapshot()},
    )


@router.api_route(
    "/projects/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse
)
async def project_detail(
    request: Request, slug: str, content: Content, repo_stats: StatsCache
) -> HTMLResponse:
    project = content.project(slug)
    if project is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "pages/project.html",
        {
            "project": project,
            "stats": repo_stats.get(project.slug),
            "devlog": content.devlog_for(project),
        },
    )

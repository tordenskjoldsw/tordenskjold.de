from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from portfolio.models import LegalLanguage, LegalTexts, SiteContent
from portfolio.services.content import get_legal_texts, get_site_content
from portfolio.services.github import RepoStatsCache, get_repo_stats
from portfolio.templating import templates

LATEST_DEVLOG_COUNT = 3
# Keeps the home page short as projects are added; /projects lists all.
HOME_PROJECT_LIMIT = 4

# The German legal texts are the binding ones and keep the original URLs;
# the English versions add a suffix. Maps language to (suffix, label).
LEGAL_VERSIONS: dict[LegalLanguage, tuple[str, str]] = {
    "de": ("", "Deutsch"),
    "en": ("/en", "English"),
}
IMPRINT_TITLES: dict[LegalLanguage, str] = {"de": "Impressum", "en": "Imprint"}
PRIVACY_TITLES: dict[LegalLanguage, str] = {
    "de": "Datenschutzerklärung",
    "en": "Privacy Policy",
}

router = APIRouter(include_in_schema=False)
Content = Annotated[SiteContent, Depends(get_site_content)]
StatsCache = Annotated[RepoStatsCache, Depends(get_repo_stats)]
Legal = Annotated[LegalTexts, Depends(get_legal_texts)]


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


@router.api_route("/imprint", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def imprint(request: Request, legal: Legal) -> HTMLResponse:
    return _legal_page(request, "/imprint", IMPRINT_TITLES, legal.imprint, "de")


@router.api_route("/imprint/en", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def imprint_english(request: Request, legal: Legal) -> HTMLResponse:
    return _legal_page(request, "/imprint", IMPRINT_TITLES, legal.imprint, "en")


@router.api_route("/privacy", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def privacy(request: Request, legal: Legal) -> HTMLResponse:
    return _legal_page(request, "/privacy", PRIVACY_TITLES, legal.privacy, "de")


@router.api_route("/privacy/en", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def privacy_english(request: Request, legal: Legal) -> HTMLResponse:
    return _legal_page(request, "/privacy", PRIVACY_TITLES, legal.privacy, "en")


def _legal_page(
    request: Request,
    path: str,
    titles: dict[LegalLanguage, str],
    texts: dict[LegalLanguage, str],
    language: LegalLanguage,
) -> HTMLResponse:
    versions = [
        {"language": code, "label": label, "href": path + suffix}
        for code, (suffix, label) in LEGAL_VERSIONS.items()
    ]
    return templates.TemplateResponse(
        request,
        "pages/legal.html",
        {
            "title": titles[language],
            "language": language,
            "body_html": texts[language],
            "versions": versions,
        },
    )

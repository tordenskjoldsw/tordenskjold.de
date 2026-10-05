from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from portfolio.config import get_app_settings
from portfolio.services.content import get_site_content
from portfolio.static_files import StaticUrls, build_static_versions

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
GITHUB_PROFILE_URL = "https://github.com/tordenskjoldsw"


# base.html needs these on every page: navigation and footer link the
# devlog only when it has entries, and canonical and Open Graph URLs must
# be absolute.
def site_context(request: Request) -> dict[str, object]:
    return {
        "has_devlog": bool(get_site_content(request).devlog),
        "base_url": get_app_settings(request).base_url,
    }


templates = Jinja2Templates(
    directory=PACKAGE_DIR / "templates", context_processors=[site_context]
)


# Root-relative paths instead of Starlette's url_for, which builds absolute
# URLs that depend on the scheme and host seen behind the reverse proxy.
templates.env.globals["static_url"] = StaticUrls(build_static_versions(STATIC_DIR))
templates.env.globals["github_profile_url"] = GITHUB_PROFILE_URL

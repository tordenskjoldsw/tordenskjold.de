from pathlib import Path

from fastapi.templating import Jinja2Templates

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
STATIC_URL_PREFIX = "/static"

templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")


# Root-relative paths instead of Starlette's url_for, which builds absolute
# URLs that depend on the scheme and host seen behind the reverse proxy.
def static_url(path: str) -> str:
    return f"{STATIC_URL_PREFIX}/{path}"


templates.env.globals["static_url"] = static_url

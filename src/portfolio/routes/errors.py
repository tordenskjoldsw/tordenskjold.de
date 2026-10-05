from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException

from portfolio.templating import templates


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_error)
    # Starlette re-raises after this handler runs, so the server still logs
    # the traceback while the visitor only sees the error page.
    app.add_exception_handler(Exception, server_error)


async def http_error(request: Request, exc: Exception) -> HTMLResponse:
    if not isinstance(exc, HTTPException):
        return await server_error(request, exc)
    return render_error(request, exc.status_code, exc.headers)


async def server_error(request: Request, exc: Exception) -> HTMLResponse:
    return render_error(request, 500)


def render_error(
    request: Request, status_code: int, headers: Mapping[str, str] | None = None
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "pages/error.html",
        {"status_code": status_code},
        status_code=status_code,
        headers=headers,
    )

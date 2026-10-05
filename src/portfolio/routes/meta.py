from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(include_in_schema=False)


# FastAPI does not add HEAD to GET routes on its own, and uptime checks use it.
@router.api_route("/health", methods=["GET", "HEAD"], response_class=PlainTextResponse)
async def health() -> str:
    return "ok"

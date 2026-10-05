import hashlib
import os
from pathlib import Path

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

STATIC_URL_PREFIX = "/static"
VERSION_LENGTH = 12

# Every page references static files with a content hash in the URL, so a
# changed file gets a new URL and browsers may keep the old one forever.
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"


class CachedStaticFiles(StaticFiles):
    def file_response(
        self,
        full_path: str | os.PathLike[str],
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = IMMUTABLE_CACHE_CONTROL
        return response


def build_static_versions(static_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(static_dir).as_posix(): _content_hash(path)
        for path in sorted(static_dir.rglob("*"))
        if path.is_file()
    }


class StaticUrls:
    def __init__(self, versions: dict[str, str]) -> None:
        self.versions = versions

    def __call__(self, path: str) -> str:
        # A KeyError for an unknown file fails the render, so a typo in a
        # template cannot ship a broken link.
        return f"{STATIC_URL_PREFIX}/{path}?v={self.versions[path]}"


def _content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:VERSION_LENGTH]

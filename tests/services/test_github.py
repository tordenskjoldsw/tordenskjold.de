import asyncio
import datetime
from collections.abc import Callable

import httpx2
import pytest
from pydantic import HttpUrl, SecretStr

from portfolio.models import Project, RepoStats
from portfolio.services.github import (
    RepoStatsCache,
    create_client,
    fetch_repo_stats,
    refresh,
    refresh_forever,
    repo_path,
)

Handler = Callable[[httpx2.Request], httpx2.Response]

REPO_JSON = {"pushed_at": "2026-10-01T12:00:00Z", "stargazers_count": 3}
RELEASE_JSON = {
    "tag_name": "v1.0.1",
    "html_url": "https://github.com/owner/name/releases/tag/v1.0.1",
    "published_at": "2026-08-05T08:31:01Z",
}


def project(slug: str, repository: str | None) -> Project:
    return Project(
        slug=slug,
        title=slug,
        summary="S",
        platform="P",
        order=1,
        repository=HttpUrl(repository) if repository else None,
        body_html="",
    )


def github(release_status: int = 200, repo_status: int = 200) -> Handler:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if request.url.path.endswith("/releases/latest"):
            return httpx2.Response(release_status, json=RELEASE_JSON)
        return httpx2.Response(repo_status, json=REPO_JSON)

    return handler


def mock_client(handler: Handler) -> httpx2.AsyncClient:
    return httpx2.AsyncClient(
        base_url="https://api.github.com", transport=httpx2.MockTransport(handler)
    )


async def stats_for(handler: Handler) -> RepoStats:
    async with mock_client(handler) as client:
        return await fetch_repo_stats(client, "owner/name")


async def refreshed(handler: Handler, cache: RepoStatsCache) -> RepoStatsCache:
    async with mock_client(handler) as client:
        await refresh(cache, client, (project("alpha", "https://github.com/o/n"),))
    return cache


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/owner/name", "owner/name"),
        ("https://github.com/owner/name/", "owner/name"),
        ("https://github.com/owner/name/tree/main", None),
        ("https://gitlab.com/owner/name", None),
    ],
)
def test_repo_path(url: str, expected: str | None) -> None:
    assert repo_path(HttpUrl(url)) == expected


def test_fetches_last_push_and_latest_release() -> None:
    stats = asyncio.run(stats_for(github()))

    assert stats.last_push == datetime.date(2026, 10, 1)
    assert stats.latest_release is not None
    assert stats.latest_release.tag_name == "v1.0.1"


def test_repository_without_release() -> None:
    stats = asyncio.run(stats_for(github(release_status=404)))

    assert stats.latest_release is None


def test_refresh_fills_cache() -> None:
    cache = asyncio.run(refreshed(github(), RepoStatsCache()))

    assert cache.get("alpha") is not None


def test_refresh_skips_projects_without_github_repository() -> None:
    async def run() -> RepoStatsCache:
        cache = RepoStatsCache()
        async with mock_client(github()) as client:
            projects = (
                project("none", None),
                project("other", "https://example.com/o/n"),
            )
            await refresh(cache, client, projects)
        return cache

    assert asyncio.run(run()).snapshot() == {}


def test_github_error_keeps_previous_stats(caplog: pytest.LogCaptureFixture) -> None:
    cache = asyncio.run(refreshed(github(), RepoStatsCache()))
    before = cache.get("alpha")

    asyncio.run(refreshed(github(repo_status=500), cache))

    assert cache.get("alpha") == before
    assert "GitHub refresh failed for o/n" in caplog.text


def test_unreachable_github_leaves_cache_empty() -> None:
    def unreachable(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("unreachable", request=request)

    cache = asyncio.run(refreshed(unreachable, RepoStatsCache()))

    assert cache.get("alpha") is None


def test_unexpected_response_is_ignored() -> None:
    def broken(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json={"unexpected": True})

    cache = asyncio.run(refreshed(broken, RepoStatsCache()))

    assert cache.get("alpha") is None


class SignallingCache(RepoStatsCache):
    def __init__(self) -> None:
        super().__init__()
        self.updated = asyncio.Event()

    def update(self, slug: str, stats: RepoStats) -> None:
        super().update(slug, stats)
        self.updated.set()


def test_refresh_forever_refreshes_until_cancelled() -> None:
    async def run() -> RepoStatsCache:
        cache = SignallingCache()
        async with mock_client(github()) as client:
            projects = (project("alpha", "https://github.com/o/n"),)
            task = asyncio.create_task(refresh_forever(cache, client, projects, 3600))
            await asyncio.wait_for(cache.updated.wait(), timeout=1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        return cache

    assert asyncio.run(run()).get("alpha") is not None


@pytest.mark.parametrize(
    ("token", "expected"), [(SecretStr("secret"), "Bearer secret"), (None, None)]
)
def test_client_sends_token_only_when_set(
    token: SecretStr | None, expected: str | None
) -> None:
    async def run() -> str | None:
        async with create_client(token, timeout=1.0) as client:
            return client.headers.get("Authorization")

    assert asyncio.run(run()) == expected

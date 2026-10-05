import asyncio
import logging
import re

import httpx2
from fastapi import Request
from pydantic import HttpUrl, SecretStr, ValidationError

from portfolio.models import GitHubRelease, GitHubRepo, Project, RepoStats

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"
GITHUB_HOST = "github.com"
REPO_PATH_PATTERN = re.compile(r"^/(?P<repo>[\w.-]+/[\w.-]+)/?$")
NOT_FOUND = 404


class RepoStatsCache:
    """Latest known stats per project slug; pages only ever read from here."""

    def __init__(self) -> None:
        self._stats: dict[str, RepoStats] = {}

    def get(self, slug: str) -> RepoStats | None:
        return self._stats.get(slug)

    def snapshot(self) -> dict[str, RepoStats]:
        return dict(self._stats)

    def update(self, slug: str, stats: RepoStats) -> None:
        self._stats[slug] = stats


def create_client(token: SecretStr | None, timeout: float) -> httpx2.AsyncClient:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "portfolio-site",
    }
    if token is not None:
        headers["Authorization"] = f"Bearer {token.get_secret_value()}"
    return httpx2.AsyncClient(base_url=GITHUB_API_URL, headers=headers, timeout=timeout)


def repo_path(repository: HttpUrl) -> str | None:
    if repository.host != GITHUB_HOST or repository.path is None:
        return None
    match = REPO_PATH_PATTERN.match(repository.path)
    return match["repo"] if match else None


async def fetch_repo_stats(client: httpx2.AsyncClient, repo: str) -> RepoStats:
    response = await client.get(f"/repos/{repo}")
    response.raise_for_status()
    repo_data = GitHubRepo.model_validate_json(response.content)
    return RepoStats(
        last_push=repo_data.pushed_at.date(),
        latest_release=await fetch_latest_release(client, repo),
    )


async def fetch_latest_release(
    client: httpx2.AsyncClient, repo: str
) -> GitHubRelease | None:
    response = await client.get(f"/repos/{repo}/releases/latest")
    # GitHub answers 404 for repositories without any release.
    if response.status_code == NOT_FOUND:
        return None
    response.raise_for_status()
    return GitHubRelease.model_validate_json(response.content)


async def refresh(
    cache: RepoStatsCache, client: httpx2.AsyncClient, projects: tuple[Project, ...]
) -> None:
    for project in projects:
        repo = repo_path(project.repository) if project.repository else None
        if repo is None:
            continue
        try:
            cache.update(project.slug, await fetch_repo_stats(client, repo))
        except (httpx2.HTTPError, ValidationError) as exc:
            # Keep the previous stats; pages fall back to showing nothing.
            logger.warning("GitHub refresh failed for %s: %s", repo, exc)


async def refresh_forever(
    cache: RepoStatsCache,
    client: httpx2.AsyncClient,
    projects: tuple[Project, ...],
    interval_seconds: int,
) -> None:
    while True:
        await refresh(cache, client, projects)
        await asyncio.sleep(interval_seconds)


def get_repo_stats(request: Request) -> RepoStatsCache:
    cache: RepoStatsCache = request.app.state.repo_stats
    return cache

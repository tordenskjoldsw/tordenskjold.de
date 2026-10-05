import datetime
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import HttpUrl

from portfolio.config import Settings
from portfolio.main import create_app
from portfolio.models import GitHubRelease, RepoStats

STATS = RepoStats(
    last_push=datetime.date(2026, 10, 1),
    latest_release=GitHubRelease(
        tag_name="v1.0.1",
        html_url=HttpUrl("https://github.com/tordenskjoldsw/PineForge/releases/v1.0.1"),
        published_at=datetime.datetime(2026, 8, 5, tzinfo=datetime.UTC),
    ),
)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
def stats_client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        app.state.repo_stats.update("pineforge", STATS)
        yield client


def test_project_list_shows_latest_release(stats_client: TestClient) -> None:
    html = stats_client.get("/").text

    assert " · v1.0.1" in html


def test_project_page_shows_release_and_last_push(stats_client: TestClient) -> None:
    html = stats_client.get("/projects/pineforge").text

    assert 'href="https://github.com/tordenskjoldsw/PineForge/releases/v1.0.1"' in html
    assert "2026-08-05" in html
    assert "<dd>2026-10-01</dd>" in html


def test_pages_render_without_github_data(client: TestClient) -> None:
    home = client.get("/")
    project = client.get("/projects/pineforge")

    assert home.status_code == project.status_code == 200
    assert "v1.0.1" not in home.text
    assert "Last push" not in project.text

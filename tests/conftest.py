from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import HttpUrl

from portfolio.config import Settings
from portfolio.main import create_app
from tests.content_helpers import SAMPLE_CERTIFICATIONS, write_entry

# Host header that TestClient sends by default.
TEST_HOST = "testserver"


@pytest.fixture
def settings() -> Settings:
    # Tests never touch the network; GitHub tests use a mocked transport.
    return Settings(
        environment="development", allowed_hosts=[TEST_HOST], github_enabled=False
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def sample_content_dir(tmp_path: Path) -> Path:
    """Content with devlog entries, which the repository does not have yet."""
    write_entry(
        tmp_path / "projects",
        "alpha",
        "title: Alpha\nsummary: First project\nplatform: Example OS\norder: 1",
        "Alpha **body**\n",
    )
    write_entry(
        tmp_path / "devlog",
        "older",
        "title: Older entry\nsummary: Older\ndate: 2026-01-01",
    )
    write_entry(
        tmp_path / "devlog",
        "newer",
        "title: Newer entry\nsummary: Newer\ndate: 2026-02-01\nproject: alpha",
        "Some <b>body</b>\n",
    )
    (tmp_path / "certifications.yaml").write_text(SAMPLE_CERTIFICATIONS)
    return tmp_path


@pytest.fixture
def sample_client(settings: Settings, sample_content_dir: Path) -> Iterator[TestClient]:
    sample_settings = settings.model_copy(
        update={
            "content_dir": sample_content_dir,
            "site_url": HttpUrl("https://example.com"),
        }
    )
    with TestClient(create_app(sample_settings)) as test_client:
        yield test_client

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from portfolio.config import Settings
from portfolio.main import create_app
from portfolio.services.content import ContentError

DOCS_PATHS = ["/docs", "/redoc", "/openapi.json"]


def test_unknown_host_is_rejected(client: TestClient) -> None:
    response = client.get("/health", headers={"host": "attacker.example"})

    assert response.status_code == 400


@pytest.mark.parametrize("path", DOCS_PATHS)
def test_docs_disabled_in_production(settings: Settings, path: str) -> None:
    production = settings.model_copy(update={"environment": "production"})

    with TestClient(create_app(production)) as client:
        assert client.get(path).status_code == 404


@pytest.mark.parametrize("path", DOCS_PATHS)
def test_docs_enabled_in_development(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200


def test_invalid_content_fails_startup(settings: Settings, tmp_path: Path) -> None:
    broken = settings.model_copy(update={"content_dir": tmp_path})

    with pytest.raises(ContentError), TestClient(create_app(broken)):
        pass


def test_server_error_shows_error_page(settings: Settings) -> None:
    app = create_app(settings)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("internal detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    assert "Something went wrong" in response.text
    assert "internal detail" not in response.text

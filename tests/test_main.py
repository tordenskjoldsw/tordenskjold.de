import pytest
from fastapi.testclient import TestClient

from portfolio.config import Settings
from portfolio.main import create_app

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

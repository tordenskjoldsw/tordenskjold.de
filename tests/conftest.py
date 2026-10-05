from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from portfolio.config import Settings
from portfolio.main import create_app

# Host header that TestClient sends by default.
TEST_HOST = "testserver"


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="development", allowed_hosts=[TEST_HOST])


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client

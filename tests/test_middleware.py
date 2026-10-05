import pytest
from fastapi.testclient import TestClient

from portfolio.middleware import SECURITY_HEADERS


@pytest.mark.parametrize(
    "path", ["/", "/projects/sailvault", "/does-not-exist", "/health"]
)
def test_security_headers_on_every_response(client: TestClient, path: str) -> None:
    response = client.get(path)

    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_security_headers_on_static_files(client: TestClient) -> None:
    response = client.get("/static/css/base.css")

    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_security_headers_on_rejected_host(client: TestClient) -> None:
    response = client.get("/", headers={"host": "attacker.example"})

    assert response.status_code == 400
    assert "Content-Security-Policy" in response.headers


def test_csp_allows_no_inline_code(client: TestClient) -> None:
    csp = client.get("/").headers["Content-Security-Policy"]

    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp
    assert "default-src 'none'" in csp

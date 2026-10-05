from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.text == "ok"


def test_health_supports_head(client: TestClient) -> None:
    response = client.head("/health")

    assert response.status_code == 200
    assert response.text == ""

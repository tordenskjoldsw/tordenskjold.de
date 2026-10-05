from fastapi.testclient import TestClient

SECTION_IDS = ["projects", "engineering", "certifications", "about"]


def test_home_renders_content(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "<h1" in response.text
    assert "SailVault" in response.text
    assert "PineForge" in response.text
    assert "4A0-100" in response.text


def test_home_has_single_h1(client: TestClient) -> None:
    response = client.get("/")

    assert response.text.count("<h1") == 1


def test_home_sections_in_order(client: TestClient) -> None:
    html = client.get("/").text

    positions = [html.index(f'id="{section_id}"') for section_id in SECTION_IDS]

    assert positions == sorted(positions)


def test_home_supports_head(client: TestClient) -> None:
    response = client.head("/")

    assert response.status_code == 200
    assert response.text == ""


def test_stylesheet_is_served(client: TestClient) -> None:
    response = client.get("/static/css/tokens.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")

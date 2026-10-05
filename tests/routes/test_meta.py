import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

SITEMAP = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.text == "ok"


def test_health_supports_head(client: TestClient) -> None:
    response = client.head("/health")

    assert response.status_code == 200
    assert response.text == ""


def test_robots_points_to_sitemap(sample_client: TestClient) -> None:
    response = sample_client.get("/robots.txt")

    assert response.status_code == 200
    assert "Sitemap: https://example.com/sitemap.xml" in response.text


def test_sitemap_lists_pages(sample_client: TestClient) -> None:
    response = sample_client.get("/sitemap.xml")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    sitemap = ET.fromstring(response.text)  # noqa: S314 - parses our own output
    locations = [loc.text for loc in sitemap.iter(f"{SITEMAP}loc")]
    assert locations == [
        "https://example.com/",
        "https://example.com/projects",
        "https://example.com/projects/alpha",
        "https://example.com/devlog",
        "https://example.com/devlog/newer",
        "https://example.com/devlog/older",
    ]

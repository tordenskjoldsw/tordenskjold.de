from fastapi.testclient import TestClient

SECTION_IDS = ["projects", "about"]


def test_home_renders_content(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "SailVault" in response.text
    assert "PineForge" in response.text
    assert "https://github.com/tordenskjoldsw/PineForge" in response.text
    assert "4A0-100" in response.text


def test_home_groups_projects_by_platform(client: TestClient) -> None:
    html = client.get("/").text

    assert html.index("Sailfish OS") < html.index("SailVault")
    assert html.index("PineTime") < html.index("PineForge")


def test_home_links_project_detail_pages(client: TestClient) -> None:
    html = client.get("/").text

    assert 'href="/projects/sailvault"' in html
    assert 'href="/projects/pineforge"' in html


def test_home_links_github_profile(client: TestClient) -> None:
    response = client.get("/")

    assert 'href="https://github.com/tordenskjoldsw"' in response.text


def test_home_has_single_h1(client: TestClient) -> None:
    response = client.get("/")

    assert response.text.count("<h1") == 1


def test_home_sections_in_order(sample_client: TestClient) -> None:
    html = sample_client.get("/").text

    positions = [html.index(f'id="{id_}"') for id_ in ["projects", "devlog", "about"]]

    assert positions == sorted(positions)


def test_home_hides_devlog_without_entries(client: TestClient) -> None:
    html = client.get("/").text

    assert 'id="devlog"' not in html
    assert 'href="/devlog"' not in html
    assert 'href="/feed.xml"' not in html


def test_home_shows_latest_devlog_entries(sample_client: TestClient) -> None:
    html = sample_client.get("/").text

    assert html.index("Newer entry") < html.index("Older entry")
    assert 'href="/devlog"' in html
    assert 'href="/feed.xml"' in html


def test_home_supports_head(client: TestClient) -> None:
    response = client.head("/")

    assert response.status_code == 200
    assert response.text == ""


def test_project_page_renders(client: TestClient) -> None:
    response = client.get("/projects/sailvault")

    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert "KeePass-compatible password manager" in response.text
    assert "License: MIT" in response.text
    assert "screenshot-1-entries.jpg" in response.text


def test_project_page_lists_its_devlog(sample_client: TestClient) -> None:
    html = sample_client.get("/projects/alpha").text

    assert "Newer entry" in html
    assert "Older entry" not in html


def test_unknown_project_returns_404_page(client: TestClient) -> None:
    response = client.get("/projects/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "Page not found" in response.text


def test_stylesheet_is_served(client: TestClient) -> None:
    response = client.get("/static/css/tokens.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")

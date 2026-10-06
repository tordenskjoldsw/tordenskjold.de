import re
from pathlib import Path

from fastapi.testclient import TestClient

from portfolio.config import Settings
from portfolio.main import create_app
from portfolio.routes.pages import HOME_PROJECT_LIMIT
from portfolio.templating import SOURCE_URL
from tests.content_helpers import write_entry


def test_home_renders_content(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "SailVault" in response.text
    assert "PineForge" in response.text
    assert "4A0-100" in response.text
    assert 'href="https://www.credly.com/badges/' in response.text


def test_footer_links_source_code(client: TestClient) -> None:
    html = client.get("/").text

    assert f'href="{SOURCE_URL}">Source of this site</a>' in html


def test_project_list_shows_platform_and_tech(client: TestClient) -> None:
    html = client.get("/").text

    assert "Sailfish OS · Rust · C++ · Qt · QML" in html
    assert "PineTime · Rust · Embassy" in html


def test_home_links_project_detail_pages(client: TestClient) -> None:
    html = client.get("/").text

    assert 'href="/projects/sailvault"' in html
    assert 'href="/projects/pineforge"' in html


def test_project_icons_are_decorative(client: TestClient) -> None:
    html = client.get("/").text

    assert re.search(
        r'<img src="/static/img/projects/sailvault/icon\.svg\?v=\w+" alt=""', html
    )
    assert '<span class="monogram" aria-hidden="true">P</span>' in html


def test_home_links_github_profile(client: TestClient) -> None:
    response = client.get("/")

    assert 'href="https://github.com/tordenskjoldsw"' in response.text


def test_home_has_single_h1(client: TestClient) -> None:
    response = client.get("/")

    assert response.text.count("<h1") == 1


def test_home_sections_in_order(sample_client: TestClient) -> None:
    html = sample_client.get("/").text

    positions = [html.index(f'id="{id_}"') for id_ in ["about", "projects", "devlog"]]

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
    assert "<dd>MIT</dd>" in response.text
    assert 'href="https://github.com/tordenskjoldsw/harbour-sailvault"' in response.text
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


def test_projects_page_lists_all_projects(client: TestClient) -> None:
    response = client.get("/projects")

    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert 'href="/projects/sailvault"' in response.text
    assert 'href="/projects/pineforge"' in response.text


def test_home_hides_all_projects_link_when_all_fit(client: TestClient) -> None:
    html = client.get("/").text

    assert 'href="/projects">All projects</a>' not in html


def test_home_limits_projects_and_links_the_rest(
    settings: Settings, sample_content_dir: Path
) -> None:
    for number in range(HOME_PROJECT_LIMIT):
        write_entry(
            sample_content_dir / "projects",
            f"extra-{number}",
            f"title: Extra {number}\nsummary: S\nplatform: P\norder: {number + 2}",
        )
    app = create_app(settings.model_copy(update={"content_dir": sample_content_dir}))

    with TestClient(app) as client:
        home = client.get("/").text
        overview = client.get("/projects").text

    assert home.count('class="project-item"') == HOME_PROJECT_LIMIT
    assert 'href="/projects">All projects</a>' in home
    assert overview.count('class="project-item"') == HOME_PROJECT_LIMIT + 1

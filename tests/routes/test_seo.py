import re

from fastapi.testclient import TestClient


def meta_content(html: str, prop: str) -> str:
    match = re.search(rf'<meta property="{re.escape(prop)}" content="([^"]*)"', html)
    assert match, f"missing {prop}"
    return match.group(1)


def page_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html)
    assert match, "missing title"
    return match.group(1)


def test_home_has_canonical_and_open_graph(sample_client: TestClient) -> None:
    html = sample_client.get("/").text

    assert '<link rel="canonical" href="https://example.com/">' in html
    assert meta_content(html, "og:type") == "website"
    assert meta_content(html, "og:url") == "https://example.com/"
    assert meta_content(html, "og:title").startswith("Tobias Kaminski")


def test_project_page_shares_cover_image(client: TestClient) -> None:
    html = client.get("/projects/sailvault").text

    image = meta_content(html, "og:image")
    assert re.fullmatch(
        r"http://localhost:8000/static/img/projects/sailvault/cover\.png\?v=\w+",
        image,
    )
    assert meta_content(html, "og:description") == (
        "KeePass-compatible password manager for Sailfish OS"
    )


def test_devlog_entry_is_an_article(sample_client: TestClient) -> None:
    html = sample_client.get("/devlog/newer").text

    assert meta_content(html, "og:type") == "article"
    assert meta_content(html, "article:published_time") == "2026-02-01"


def test_error_page_is_not_indexed(client: TestClient) -> None:
    html = client.get("/does-not-exist").text

    assert '<meta name="robots" content="noindex">' in html
    assert 'rel="canonical"' not in html


def test_pages_have_unique_titles(sample_client: TestClient) -> None:
    paths = ["/", "/projects/alpha", "/devlog", "/devlog/newer"]

    titles = {page_title(sample_client.get(path).text) for path in paths}

    assert len(titles) == len(paths)

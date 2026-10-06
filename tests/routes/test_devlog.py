import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

ATOM = "{http://www.w3.org/2005/Atom}"


def test_devlog_index_lists_entries_newest_first(sample_client: TestClient) -> None:
    response = sample_client.get("/devlog")

    assert response.status_code == 200
    assert response.text.index("Newer entry") < response.text.index("Older entry")


def test_devlog_index_without_entries(no_devlog_client: TestClient) -> None:
    response = no_devlog_client.get("/devlog")

    assert response.status_code == 200
    assert "No entries yet." in response.text


def test_devlog_entry_renders(sample_client: TestClient) -> None:
    response = sample_client.get("/devlog/newer")

    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert 'href="/projects/alpha"' in response.text
    assert "&lt;b&gt;body&lt;/b&gt;" in response.text


def test_unknown_devlog_entry_returns_404(sample_client: TestClient) -> None:
    assert sample_client.get("/devlog/does-not-exist").status_code == 404


def test_feed_is_valid_atom(sample_client: TestClient) -> None:
    response = sample_client.get("/feed.xml")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/atom+xml")
    feed = ET.fromstring(response.text)  # noqa: S314 - parses our own output
    assert feed.findtext(f"{ATOM}updated") == "2026-02-01T00:00:00Z"
    ids = [entry.findtext(f"{ATOM}id") for entry in feed.iter(f"{ATOM}entry")]
    assert ids == [
        "https://example.com/devlog/newer",
        "https://example.com/devlog/older",
    ]


def test_feed_returns_404_without_entries(no_devlog_client: TestClient) -> None:
    assert no_devlog_client.get("/feed.xml").status_code == 404

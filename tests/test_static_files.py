import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from portfolio.static_files import (
    IMMUTABLE_CACHE_CONTROL,
    StaticUrls,
    build_static_versions,
)


def test_versions_change_with_content(tmp_path: Path) -> None:
    (tmp_path / "css").mkdir()
    style = tmp_path / "css" / "site.css"
    style.write_text("a {}")
    before = build_static_versions(tmp_path)["css/site.css"]

    style.write_text("a { color: red; }")

    assert build_static_versions(tmp_path)["css/site.css"] != before


def test_static_url_contains_version() -> None:
    static_url = StaticUrls({"css/site.css": "abc123"})

    assert static_url("css/site.css") == "/static/css/site.css?v=abc123"


def test_static_url_rejects_unknown_file() -> None:
    static_url = StaticUrls({})

    with pytest.raises(KeyError):
        static_url("css/missing.css")


def test_pages_reference_versioned_assets(client: TestClient) -> None:
    html = client.get("/").text

    assert re.search(r'href="/static/css/base\.css\?v=[0-9a-f]{12}"', html)
    assert re.search(r'src="/static/img/projects/sailvault/icon\.svg\?v=', html)


def test_static_files_are_cached_long_term(client: TestClient) -> None:
    response = client.get("/static/css/base.css")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == IMMUTABLE_CACHE_CONTROL

from pathlib import Path

from portfolio.services.content import load_content
from portfolio.services.sitemap import sitemap_entries
from portfolio.templating import STATIC_DIR


def test_sitemap_omits_devlog_without_entries(sample_content_dir: Path) -> None:
    for entry in (sample_content_dir / "devlog").iterdir():
        entry.unlink()
    content = load_content(sample_content_dir, STATIC_DIR)

    paths = [entry.path for entry in sitemap_entries(content)]

    assert paths == ["/", "/projects", "/projects/alpha"]


def test_sitemap_dates_devlog_entries(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    lastmod = {entry.path: entry.lastmod for entry in sitemap_entries(content)}

    assert str(lastmod["/devlog"]) == "2026-02-01"
    assert str(lastmod["/devlog/older"]) == "2026-01-01"

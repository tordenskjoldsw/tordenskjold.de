from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from portfolio.config import EXAMPLE_LEGAL_DIR, Settings
from portfolio.main import create_app
from portfolio.services.content import ContentError

LEGAL_PAGES = [
    ("/imprint", "Impressum", "de"),
    ("/imprint/en", "Imprint", "en"),
    ("/privacy", "Datenschutzerklärung", "de"),
    ("/privacy/en", "Privacy Policy", "en"),
]
LEGAL_FILES = ["imprint.md", "imprint.en.md", "privacy.md", "privacy.en.md"]


@pytest.mark.parametrize(("path", "title", "language"), LEGAL_PAGES)
def test_legal_page_renders(
    client: TestClient, path: str, title: str, language: str
) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert f"{title}</h1>" in response.text
    assert f'<article class="column page" lang="{language}">' in response.text


@pytest.mark.parametrize(("path", "title", "language"), LEGAL_PAGES)
def test_legal_page_shows_its_own_text(
    client: TestClient, path: str, title: str, language: str
) -> None:
    html = client.get(path).text

    assert ("Name und Anschrift" in html) == (path == "/privacy")
    assert ("Name and address" in html) == (path == "/privacy/en")
    assert ("Angaben gemäß" in html) == (path == "/imprint")
    assert ("Information pursuant to" in html) == (path == "/imprint/en")


@pytest.mark.parametrize(("path", "title", "language"), LEGAL_PAGES)
def test_legal_page_links_both_languages(
    client: TestClient, path: str, title: str, language: str
) -> None:
    html = client.get(path).text
    base_path = path.removesuffix("/en")
    links = {
        "de": f'<a href="{base_path}" hreflang="de" lang="de"',
        "en": f'<a href="{base_path}/en" hreflang="en" lang="en"',
    }

    assert '<nav class="language-switch" aria-label="Language" lang="en">' in html
    for code, link in links.items():
        current = ' aria-current="page"' if code == language else ""
        assert f"{link}{current}>" in html
    assert html.count('aria-current="page"') == 1


@pytest.mark.parametrize(("path", "title", "language"), LEGAL_PAGES)
def test_legal_page_is_not_indexed(
    client: TestClient, path: str, title: str, language: str
) -> None:
    html = client.get(path).text

    assert '<meta name="robots" content="noindex">' in html
    assert 'rel="canonical"' not in html


@pytest.mark.parametrize("path", ["/", "/projects/sailvault", "/does-not-exist"])
def test_footer_links_legal_pages(client: TestClient, path: str) -> None:
    html = client.get(path).text

    assert 'href="/imprint">Imprint (Impressum)</a>' in html
    assert 'href="/privacy">Privacy (Datenschutz)</a>' in html


@pytest.mark.parametrize("missing", LEGAL_FILES)
def test_missing_legal_text_fails_startup(
    settings: Settings, tmp_path: Path, missing: str
) -> None:
    for name in LEGAL_FILES:
        if name != missing:
            (tmp_path / name).write_text("Text\n")
    broken = settings.model_copy(update={"legal_dir": tmp_path})

    with (
        pytest.raises(ContentError, match=missing.replace(".", r"\.")),
        TestClient(create_app(broken)),
    ):
        pass


def test_legal_text_with_own_title_fails_startup(
    settings: Settings, tmp_path: Path
) -> None:
    for name in LEGAL_FILES:
        (tmp_path / name).write_text("Text\n")
    (tmp_path / "privacy.en.md").write_text("# Privacy Policy\n\nText\n")
    broken = settings.model_copy(update={"legal_dir": tmp_path})

    with (
        pytest.raises(ContentError, match="use ## headings"),
        TestClient(create_app(broken)),
    ):
        pass


def test_production_rejects_example_legal_texts() -> None:
    with pytest.raises(ValidationError, match="LEGAL_DIR"):
        Settings(environment="production", legal_dir=EXAMPLE_LEGAL_DIR)


def test_production_accepts_real_legal_texts(tmp_path: Path) -> None:
    settings = Settings(environment="production", legal_dir=tmp_path)

    assert settings.legal_dir == tmp_path

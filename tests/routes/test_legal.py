from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from portfolio.config import EXAMPLE_LEGAL_DIR, Settings
from portfolio.main import create_app
from portfolio.services.content import ContentError

LEGAL_PAGES = [("/imprint", "Impressum"), ("/privacy", "Datenschutzerklärung")]


@pytest.mark.parametrize(("path", "title"), LEGAL_PAGES)
def test_legal_page_renders(client: TestClient, path: str, title: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert f"{title}</h1>" in response.text
    assert '<article class="column page" lang="de">' in response.text


@pytest.mark.parametrize(("path", "title"), LEGAL_PAGES)
def test_legal_page_is_not_indexed(client: TestClient, path: str, title: str) -> None:
    html = client.get(path).text

    assert '<meta name="robots" content="noindex">' in html
    assert 'rel="canonical"' not in html


@pytest.mark.parametrize("path", ["/", "/projects/sailvault", "/does-not-exist"])
def test_footer_links_legal_pages(client: TestClient, path: str) -> None:
    html = client.get(path).text

    assert 'href="/imprint">Imprint (Impressum)</a>' in html
    assert 'href="/privacy">Privacy (Datenschutz)</a>' in html


def test_missing_legal_text_fails_startup(settings: Settings, tmp_path: Path) -> None:
    (tmp_path / "imprint.md").write_text("Text\n")
    broken = settings.model_copy(update={"legal_dir": tmp_path})

    with (
        pytest.raises(ContentError, match=r"privacy\.md"),
        TestClient(create_app(broken)),
    ):
        pass


def test_legal_text_with_own_title_fails_startup(
    settings: Settings, tmp_path: Path
) -> None:
    (tmp_path / "imprint.md").write_text("# Impressum\n\nText\n")
    (tmp_path / "privacy.md").write_text("Text\n")
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

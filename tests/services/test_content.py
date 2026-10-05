from pathlib import Path

import pytest

from portfolio.services.content import ContentError, load_content

VALID_CERTIFICATIONS = """
- name: Example Certification
  exam_code: EX-100
  issuer: Example Issuer
  credential_url: https://example.com/credential
"""


def write_project(content_dir: Path, slug: str, front_matter: str) -> None:
    projects_dir = content_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    (projects_dir / f"{slug}.md").write_text(f"---\n{front_matter}\n---\n\nBody\n")


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    (tmp_path / "projects").mkdir()
    (tmp_path / "certifications.yaml").write_text(VALID_CERTIFICATIONS)
    return tmp_path


def test_loads_projects_sorted_by_order(content_dir: Path) -> None:
    write_project(content_dir, "second", "title: Second\nsummary: B\norder: 2")
    write_project(content_dir, "first", "title: First\nsummary: A\norder: 1")

    content = load_content(content_dir)

    assert [project.slug for project in content.projects] == ["first", "second"]


def test_slug_comes_from_file_name(content_dir: Path) -> None:
    write_project(
        content_dir, "real-slug", "title: T\nsummary: S\norder: 1\nslug: ignored"
    )

    content = load_content(content_dir)

    assert content.projects[0].slug == "real-slug"


def test_loads_certifications(content_dir: Path) -> None:
    content = load_content(content_dir)

    assert content.certifications[0].exam_code == "EX-100"


def test_repository_content_is_valid() -> None:
    content_dir = Path(__file__).resolve().parents[2] / "content"

    content = load_content(content_dir)

    assert content.projects
    assert content.certifications


@pytest.mark.parametrize(
    ("front_matter", "message"),
    [
        ("title: T\norder: 1", "invalid front matter"),
        ("title: T\nsummary: S\norder: first", "invalid front matter"),
        ("title: T\nsummary: S\norder: 1\nunknown: x", "invalid front matter"),
        ("title: [unclosed", "invalid YAML"),
        ("- just\n- a list", "front matter must be a mapping"),
    ],
)
def test_invalid_front_matter_fails(
    content_dir: Path, front_matter: str, message: str
) -> None:
    write_project(content_dir, "broken", front_matter)

    with pytest.raises(ContentError, match=message) as error:
        load_content(content_dir)

    assert "broken.md" in str(error.value)


def test_missing_front_matter_fails(content_dir: Path) -> None:
    (content_dir / "projects" / "plain.md").write_text("No front matter\n")

    with pytest.raises(ContentError, match="missing YAML front matter"):
        load_content(content_dir)


def test_invalid_slug_fails(content_dir: Path) -> None:
    write_project(content_dir, "Not_A_Slug", "title: T\nsummary: S\norder: 1")

    with pytest.raises(ContentError, match="invalid front matter"):
        load_content(content_dir)


def test_missing_projects_directory_fails(content_dir: Path) -> None:
    (content_dir / "projects").rmdir()

    with pytest.raises(ContentError, match="projects directory not found"):
        load_content(content_dir)


def test_missing_certifications_file_fails(content_dir: Path) -> None:
    (content_dir / "certifications.yaml").unlink()

    with pytest.raises(ContentError, match="cannot read file"):
        load_content(content_dir)


def test_invalid_certification_url_fails(content_dir: Path) -> None:
    (content_dir / "certifications.yaml").write_text(
        VALID_CERTIFICATIONS.replace("https://example.com/credential", "not a url")
    )

    with pytest.raises(ContentError, match="invalid certifications"):
        load_content(content_dir)

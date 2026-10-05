from pathlib import Path

import pytest

from portfolio.config import DEFAULT_CONTENT_DIR
from portfolio.services.content import ContentError, load_content
from portfolio.templating import STATIC_DIR
from tests.content_helpers import write_entry

PROJECT = "title: T\nsummary: S\nplatform: P\norder: {order}"


def test_loads_projects_sorted_by_order(sample_content_dir: Path) -> None:
    projects_dir = sample_content_dir / "projects"
    write_entry(projects_dir, "zulu", PROJECT.format(order=0))

    content = load_content(sample_content_dir, STATIC_DIR)

    assert [project.slug for project in content.projects] == ["zulu", "alpha"]


def test_slug_comes_from_file_name(sample_content_dir: Path) -> None:
    write_entry(
        sample_content_dir / "projects",
        "real-slug",
        PROJECT.format(order=2) + "\nslug: ignored",
    )

    content = load_content(sample_content_dir, STATIC_DIR)

    assert content.project("real-slug") is not None


def test_renders_markdown_body(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    project = content.project("alpha")
    assert project is not None
    assert "<strong>body</strong>" in project.body_html


def test_raw_html_in_markdown_is_escaped(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    entry = content.devlog_entry("newer")
    assert entry is not None
    assert "<b>" not in entry.body_html
    assert "&lt;b&gt;" in entry.body_html


def test_devlog_sorted_newest_first(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    assert [entry.slug for entry in content.devlog] == ["newer", "older"]


def test_devlog_for_project(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    project = content.project("alpha")
    assert project is not None
    assert [entry.slug for entry in content.devlog_for(project)] == ["newer"]


def test_projects_grouped_by_platform_in_project_order(
    sample_content_dir: Path,
) -> None:
    projects_dir = sample_content_dir / "projects"
    write_entry(projects_dir, "beta", "title: B\nsummary: S\nplatform: Zeta\norder: 0")
    write_entry(
        projects_dir, "gamma", "title: G\nsummary: S\nplatform: Example OS\norder: 2"
    )

    groups = load_content(sample_content_dir, STATIC_DIR).projects_by_platform()

    assert [group.platform for group in groups] == ["Zeta", "Example OS"]
    assert [project.slug for project in groups[1].projects] == ["alpha", "gamma"]


def test_loads_certifications(sample_content_dir: Path) -> None:
    content = load_content(sample_content_dir, STATIC_DIR)

    assert content.certifications[0].exam_code == "EX-100"


def test_repository_content_is_valid() -> None:
    content = load_content(DEFAULT_CONTENT_DIR, STATIC_DIR)

    assert content.projects
    assert content.certifications


@pytest.mark.parametrize(
    ("front_matter", "message"),
    [
        ("title: T\nplatform: P\norder: 1", "invalid front matter"),
        ("title: T\nsummary: S\nplatform: P\norder: first", "invalid front matter"),
        (PROJECT.format(order=1) + "\nunknown: x", "invalid front matter"),
        ("title: [unclosed", "invalid YAML"),
        ("- just\n- a list", "front matter must be a mapping"),
    ],
)
def test_invalid_front_matter_fails(
    sample_content_dir: Path, front_matter: str, message: str
) -> None:
    write_entry(sample_content_dir / "projects", "broken", front_matter)

    with pytest.raises(ContentError, match=message) as error:
        load_content(sample_content_dir, STATIC_DIR)

    assert "broken.md" in str(error.value)


def test_missing_front_matter_fails(sample_content_dir: Path) -> None:
    (sample_content_dir / "projects" / "plain.md").write_text("No front matter\n")

    with pytest.raises(ContentError, match="missing YAML front matter"):
        load_content(sample_content_dir, STATIC_DIR)


def test_invalid_slug_fails(sample_content_dir: Path) -> None:
    write_entry(sample_content_dir / "projects", "Not_A_Slug", PROJECT.format(order=1))

    with pytest.raises(ContentError, match="invalid front matter"):
        load_content(sample_content_dir, STATIC_DIR)


def test_missing_image_fails(sample_content_dir: Path) -> None:
    cover = "\ncover: {path: img/missing.png, alt: A, width: 1, height: 1}"
    write_entry(
        sample_content_dir / "projects", "pictured", PROJECT.format(order=1) + cover
    )

    with pytest.raises(ContentError, match=r"missing image img/missing\.png"):
        load_content(sample_content_dir, STATIC_DIR)


def test_devlog_with_unknown_project_fails(sample_content_dir: Path) -> None:
    write_entry(
        sample_content_dir / "devlog",
        "orphan",
        "title: T\nsummary: S\ndate: 2026-03-01\nproject: nonexistent",
    )

    with pytest.raises(ContentError, match="unknown project 'nonexistent'"):
        load_content(sample_content_dir, STATIC_DIR)


def test_devlog_with_invalid_date_fails(sample_content_dir: Path) -> None:
    write_entry(
        sample_content_dir / "devlog", "undated", "title: T\nsummary: S\ndate: soon"
    )

    with pytest.raises(ContentError, match="invalid front matter"):
        load_content(sample_content_dir, STATIC_DIR)


@pytest.mark.parametrize("directory", ["projects", "devlog"])
def test_missing_directory_fails(sample_content_dir: Path, directory: str) -> None:
    for path in (sample_content_dir / directory).iterdir():
        path.unlink()
    (sample_content_dir / directory).rmdir()

    with pytest.raises(ContentError, match="directory not found"):
        load_content(sample_content_dir, STATIC_DIR)


def test_missing_certifications_file_fails(sample_content_dir: Path) -> None:
    (sample_content_dir / "certifications.yaml").unlink()

    with pytest.raises(ContentError, match="cannot read file"):
        load_content(sample_content_dir, STATIC_DIR)


def test_invalid_certification_url_fails(sample_content_dir: Path) -> None:
    path = sample_content_dir / "certifications.yaml"
    path.write_text(path.read_text().replace("https://example.com/credential", "x"))

    with pytest.raises(ContentError, match="invalid certifications"):
        load_content(sample_content_dir, STATIC_DIR)

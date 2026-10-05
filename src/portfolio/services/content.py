import re
from pathlib import Path

import yaml
from fastapi import Request
from markdown_it import MarkdownIt
from pydantic import BaseModel, TypeAdapter, ValidationError

from portfolio.models import Certification, DevlogEntry, Image, Project, SiteContent

FRONT_MATTER_PATTERN = re.compile(
    r"\A---\n(?P<yaml>.*?)\n---(?:\n(?P<body>.*))?\Z", re.DOTALL
)
CERTIFICATIONS_ADAPTER = TypeAdapter(tuple[Certification, ...])

# Raw HTML stays disabled so content files cannot smuggle markup past the
# template autoescaping that |safe bypasses.
MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable("table")


class ContentError(Exception):
    """Raised at startup when a content file is missing or invalid."""


def load_content(content_dir: Path, static_dir: Path) -> SiteContent:
    projects = load_projects(content_dir / "projects", static_dir)
    devlog = load_devlog(content_dir / "devlog", projects)
    return SiteContent(
        projects=projects,
        devlog=devlog,
        certifications=load_certifications(content_dir / "certifications.yaml"),
    )


def load_projects(directory: Path, static_dir: Path) -> tuple[Project, ...]:
    projects = [_load_entry(path, Project) for path in _markdown_files(directory)]
    for project in projects:
        _check_images_exist(project, static_dir)
    return tuple(sorted(projects, key=lambda project: project.order))


def load_devlog(
    directory: Path, projects: tuple[Project, ...]
) -> tuple[DevlogEntry, ...]:
    entries = [_load_entry(path, DevlogEntry) for path in _markdown_files(directory)]
    known_slugs = {project.slug for project in projects}
    for entry in entries:
        if entry.project is not None and entry.project not in known_slugs:
            raise ContentError(
                f"{directory / entry.slug}.md: unknown project '{entry.project}'"
            )
    return tuple(sorted(entries, key=lambda entry: entry.date, reverse=True))


def load_certifications(path: Path) -> tuple[Certification, ...]:
    data = _parse_yaml(_read_text(path), path)
    try:
        return CERTIFICATIONS_ADAPTER.validate_python(data)
    except ValidationError as exc:
        raise ContentError(f"{path}: invalid certifications\n{exc}") from exc


def get_site_content(request: Request) -> SiteContent:
    content: SiteContent = request.app.state.content
    return content


def _markdown_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ContentError(f"{directory}: directory not found")
    return sorted(directory.glob("*.md"))


def _load_entry[EntryT: BaseModel](path: Path, model: type[EntryT]) -> EntryT:
    match = FRONT_MATTER_PATTERN.match(_read_text(path))
    if match is None:
        raise ContentError(f"{path}: missing YAML front matter")
    front_matter = _parse_yaml(match["yaml"], path)
    if not isinstance(front_matter, dict):
        raise ContentError(f"{path}: front matter must be a mapping")
    # The file name is the single source of the slug, so it cannot drift
    # from a value repeated in the front matter.
    data = {
        **front_matter,
        "slug": path.stem,
        "body_html": MARKDOWN.render(match["body"] or ""),
    }
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ContentError(f"{path}: invalid front matter\n{exc}") from exc


def _check_images_exist(project: Project, static_dir: Path) -> None:
    images: list[Image] = list(project.screenshots)
    if project.cover is not None:
        images.append(project.cover)
    for image in images:
        if not (static_dir / image.path).is_file():
            raise ContentError(f"project '{project.slug}': missing image {image.path}")


def _parse_yaml(text: str, path: Path) -> object:
    try:
        data: object = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ContentError(f"{path}: invalid YAML\n{exc}") from exc
    return data


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContentError(f"{path}: cannot read file ({exc.strerror})") from exc

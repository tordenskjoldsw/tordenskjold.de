import re
from pathlib import Path

import yaml
from fastapi import Request
from pydantic import TypeAdapter, ValidationError

from portfolio.models import Certification, Project, SiteContent

FRONT_MATTER_PATTERN = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n", re.DOTALL)
CERTIFICATIONS_ADAPTER = TypeAdapter(tuple[Certification, ...])


class ContentError(Exception):
    """Raised at startup when a content file is missing or invalid."""


def load_content(content_dir: Path) -> SiteContent:
    return SiteContent(
        projects=load_projects(content_dir / "projects"),
        certifications=load_certifications(content_dir / "certifications.yaml"),
    )


def load_projects(directory: Path) -> tuple[Project, ...]:
    if not directory.is_dir():
        raise ContentError(f"{directory}: projects directory not found")
    projects = [_load_project(path) for path in sorted(directory.glob("*.md"))]
    return tuple(sorted(projects, key=lambda project: project.order))


def load_certifications(path: Path) -> tuple[Certification, ...]:
    data = _parse_yaml(_read_text(path), path)
    try:
        return CERTIFICATIONS_ADAPTER.validate_python(data)
    except ValidationError as exc:
        raise ContentError(f"{path}: invalid certifications\n{exc}") from exc


def get_site_content(request: Request) -> SiteContent:
    content: SiteContent = request.app.state.content
    return content


def _load_project(path: Path) -> Project:
    front_matter = _parse_front_matter(path)
    if not isinstance(front_matter, dict):
        raise ContentError(f"{path}: front matter must be a mapping")
    # The file name is the single source of the slug, so it cannot drift
    # from a value repeated in the front matter.
    try:
        return Project.model_validate({**front_matter, "slug": path.stem})
    except ValidationError as exc:
        raise ContentError(f"{path}: invalid front matter\n{exc}") from exc


def _parse_front_matter(path: Path) -> object:
    match = FRONT_MATTER_PATTERN.match(_read_text(path))
    if match is None:
        raise ContentError(f"{path}: missing YAML front matter")
    return _parse_yaml(match["yaml"], path)


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

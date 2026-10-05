import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt

# Slugs end up in URLs, so keep them lowercase and hyphen-separated.
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class ContentModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Image(ContentModel):
    path: str = Field(min_length=1, description="Relative to the static dir")
    alt: str = Field(min_length=1)
    width: PositiveInt
    height: PositiveInt


class Project(ContentModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    order: int
    tags: tuple[str, ...] = ()
    license: str | None = None
    repository: HttpUrl | None = None
    download: HttpUrl | None = None
    # Square, decorative next to the name, so it needs no alt text.
    icon: str | None = Field(default=None, min_length=1)
    cover: Image | None = None
    screenshots: tuple[Image, ...] = ()
    body_html: str


class DevlogEntry(ContentModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    date: datetime.date
    project: str | None = Field(default=None, pattern=SLUG_PATTERN)
    body_html: str


class Certification(ContentModel):
    name: str = Field(min_length=1)
    exam_code: str = Field(min_length=1)
    issuer: str = Field(min_length=1)
    credential_url: HttpUrl | None = None


class LegalTexts(ContentModel):
    imprint_html: str
    privacy_html: str


class SitemapEntry(ContentModel):
    path: str
    lastmod: datetime.date | None = None


class SiteContent(ContentModel):
    projects: tuple[Project, ...]
    devlog: tuple[DevlogEntry, ...]
    certifications: tuple[Certification, ...]

    def project(self, slug: str) -> Project | None:
        return next((p for p in self.projects if p.slug == slug), None)

    def devlog_entry(self, slug: str) -> DevlogEntry | None:
        return next((e for e in self.devlog if e.slug == slug), None)

    def devlog_for(self, project: Project) -> tuple[DevlogEntry, ...]:
        return tuple(e for e in self.devlog if e.project == project.slug)


class GitHubModel(BaseModel):
    # GitHub responses carry far more fields than the site uses.
    model_config = ConfigDict(frozen=True, extra="ignore")


class GitHubRepo(GitHubModel):
    pushed_at: datetime.datetime


class GitHubRelease(GitHubModel):
    tag_name: str
    html_url: HttpUrl
    published_at: datetime.datetime


class RepoStats(GitHubModel):
    last_push: datetime.date
    latest_release: GitHubRelease | None

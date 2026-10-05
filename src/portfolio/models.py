from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# Slugs end up in URLs, so keep them lowercase and hyphen-separated.
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


class ContentModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Project(ContentModel):
    slug: str = Field(pattern=SLUG_PATTERN)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    order: int
    license: str | None = None
    repository: HttpUrl | None = None


class Certification(ContentModel):
    name: str = Field(min_length=1)
    exam_code: str = Field(min_length=1)
    issuer: str = Field(min_length=1)
    credential_url: HttpUrl | None = None


class SiteContent(ContentModel):
    projects: tuple[Project, ...]
    certifications: tuple[Certification, ...]

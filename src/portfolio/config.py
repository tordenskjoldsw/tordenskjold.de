from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import Request
from pydantic import HttpUrl, PositiveFloat, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# The content directory sits at the repository root, next to src/.
DEFAULT_CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "production"] = "development"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    content_dir: Path = DEFAULT_CONTENT_DIR
    site_url: HttpUrl = HttpUrl("http://localhost:8000")

    github_enabled: bool = True
    github_token: SecretStr | None = None
    github_refresh_seconds: PositiveInt = 3600
    github_timeout_seconds: PositiveFloat = 10.0

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def base_url(self) -> str:
        return str(self.site_url).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Routes read the settings the app was created with, so tests can pass
# their own instead of the cached environment settings.
def get_app_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings

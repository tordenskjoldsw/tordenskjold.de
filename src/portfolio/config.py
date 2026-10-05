from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# The content directory sits at the repository root, next to src/.
DEFAULT_CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "production"] = "development"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    content_dir: Path = DEFAULT_CONTENT_DIR

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()

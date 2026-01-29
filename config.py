"""Configuration management for the Ad Creative Agent."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Storage
    storage_type: Literal["local", "s3"] = "local"
    storage_local_path: str = "./outputs"

    # S3 (optional)
    s3_bucket: str = ""
    s3_region: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint_url: str = ""

    # Base URL for file URLs
    base_url: str = "http://localhost:8000"

    # Image Generation Backends
    openai_api_key: str = ""
    replicate_api_token: str = ""
    stability_api_key: str = ""
    ideogram_api_key: str = ""

    # Video Generation Backends (Phase 4)
    runway_api_key: str = ""
    pika_api_key: str = ""
    kling_api_key: str = ""

    # Reference Analysis
    vision_model: str = "gpt-4o"
    serper_api_key: str = ""

    def get_available_image_backends(self) -> list[str]:
        """Return list of configured image generation backends."""
        backends = []
        if self.openai_api_key:
            backends.append("dalle3")
        if self.replicate_api_token:
            backends.extend(["flux", "sdxl"])
        if self.stability_api_key:
            backends.append("stability")
        if self.ideogram_api_key:
            backends.append("ideogram")
        return backends

    def get_available_video_backends(self) -> list[str]:
        """Return list of configured video generation backends."""
        backends = []
        if self.runway_api_key:
            backends.append("runway")
        if self.pika_api_key:
            backends.append("pika")
        if self.kling_api_key:
            backends.append("kling")
        return backends


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

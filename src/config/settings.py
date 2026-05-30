"""Configuration module handling environment variables and global application setup via Pydantic."""

import functools
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("settings",)


class Settings(BaseSettings):
    """Application settings validated and parsed from the environment variables."""

    bot_token: SecretStr
    channel_id: int
    discussion_id: int
    channel_chat_link: str

    twitch_client_id: SecretStr
    twitch_secret: SecretStr
    streamer_username: str

    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    LOCALES_PATH: Path = BASE_DIR / "locales"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@functools.lru_cache
def get_settings() -> Settings:
    """
    Initialize and cache settings instance using LRU cache strategy.

    Returns
    -------
    Settings
        The validated runtime application configuration instance.
    """
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

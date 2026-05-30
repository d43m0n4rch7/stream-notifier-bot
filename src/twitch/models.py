"""Data transfer schemas defining verified structure blocks received from Twitch API Helix."""

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ("StreamInfo", "UserInfo", "VodInfo")


class StreamInfo(BaseModel):
    """Parsed definition mapping an active live-streaming broadcast context session."""

    id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: str
    title: str
    tags: list[str] = Field(default_factory=list)
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    is_mature: bool


class UserInfo(BaseModel):
    """Structure encapsulating verified global records specific to a unique Twitch profile."""

    id: str
    login: str
    display_name: str
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int = 0
    created_at: datetime


class VodInfo(BaseModel):
    """Model mapping archival video tracking historical metadata definitions."""

    id: str
    stream_id: str | None = None
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str
    duration: str

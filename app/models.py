from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# Persistent models (stored in database)
class Video(SQLModel, table=True):
    """Video model for storing video metadata."""

    __tablename__ = "videos"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = Field(default="", max_length=2000)
    file_path: str = Field(max_length=500, description="Path to video file")
    file_size: int = Field(description="File size in bytes")
    duration: Decimal = Field(description="Video duration in seconds", default=Decimal("0"))
    width: Optional[int] = Field(default=None, description="Video width in pixels")
    height: Optional[int] = Field(default=None, description="Video height in pixels")
    frame_rate: Optional[Decimal] = Field(default=None, description="Frames per second")
    format: str = Field(max_length=50, description="Video format (mp4, avi, etc.)")
    codec: Optional[str] = Field(default=None, max_length=50, description="Video codec")
    thumbnail_path: Optional[str] = Field(default=None, max_length=500, description="Path to thumbnail image")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    playlist_items: List["PlaylistItem"] = Relationship(back_populates="video")
    playback_sessions: List["PlaybackSession"] = Relationship(back_populates="video")


class Playlist(SQLModel, table=True):
    """Playlist model for organizing videos."""

    __tablename__ = "playlists"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    is_favorite: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    items: List["PlaylistItem"] = Relationship(back_populates="playlist")


class PlaylistItem(SQLModel, table=True):
    """Junction table for playlist-video relationships with ordering."""

    __tablename__ = "playlist_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    playlist_id: int = Field(foreign_key="playlists.id")
    video_id: int = Field(foreign_key="videos.id")
    position: int = Field(description="Order of video in playlist")
    added_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    playlist: Playlist = Relationship(back_populates="items")
    video: Video = Relationship(back_populates="playlist_items")


class PlaybackSession(SQLModel, table=True):
    """Track playback sessions and resume positions."""

    __tablename__ = "playback_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="videos.id")
    current_position: Decimal = Field(default=Decimal("0"), description="Current playback position in seconds")
    volume_level: Decimal = Field(default=Decimal("100"), description="Volume level (0-100)")
    playback_speed: Decimal = Field(default=Decimal("1.0"), description="Playback speed multiplier")
    is_muted: bool = Field(default=False)
    is_fullscreen: bool = Field(default=False)
    last_played_at: datetime = Field(default_factory=datetime.utcnow)
    total_watch_time: Decimal = Field(default=Decimal("0"), description="Total time watched in seconds")
    watch_count: int = Field(default=1, description="Number of times video was played")

    # Relationships
    video: Video = Relationship(back_populates="playback_sessions")


class UserPreference(SQLModel, table=True):
    """Global user preferences for the video player."""

    __tablename__ = "user_preferences"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    preference_key: str = Field(max_length=100, unique=True, description="Preference identifier")
    preference_value: str = Field(max_length=500, description="Preference value as string")
    data_type: str = Field(max_length=20, description="Data type: string, int, float, bool, json")
    description: str = Field(default="", max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VideoTag(SQLModel, table=True):
    """Tags for categorizing videos."""

    __tablename__ = "video_tags"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    color: Optional[str] = Field(default=None, max_length=7, description="Hex color code")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    video_tag_links: List["VideoTagLink"] = Relationship(back_populates="tag")


class VideoTagLink(SQLModel, table=True):
    """Junction table for video-tag relationships."""

    __tablename__ = "video_tag_links"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="videos.id")
    tag_id: int = Field(foreign_key="video_tags.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    video: Video = Relationship()
    tag: VideoTag = Relationship(back_populates="video_tag_links")


# Non-persistent schemas (for validation, forms, API requests/responses)
class VideoCreate(SQLModel, table=False):
    """Schema for creating a new video."""

    title: str = Field(max_length=255)
    description: str = Field(default="", max_length=2000)
    file_path: str = Field(max_length=500)
    file_size: int
    duration: Decimal = Field(default=Decimal("0"))
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    frame_rate: Optional[Decimal] = Field(default=None)
    format: str = Field(max_length=50)
    codec: Optional[str] = Field(default=None, max_length=50)
    thumbnail_path: Optional[str] = Field(default=None, max_length=500)


class VideoUpdate(SQLModel, table=False):
    """Schema for updating video metadata."""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    thumbnail_path: Optional[str] = Field(default=None, max_length=500)


class PlaylistCreate(SQLModel, table=False):
    """Schema for creating a playlist."""

    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    is_favorite: bool = Field(default=False)


class PlaylistUpdate(SQLModel, table=False):
    """Schema for updating playlist."""

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_favorite: Optional[bool] = Field(default=None)


class PlaylistItemCreate(SQLModel, table=False):
    """Schema for adding video to playlist."""

    playlist_id: int
    video_id: int
    position: int


class PlaybackSessionUpdate(SQLModel, table=False):
    """Schema for updating playback session."""

    current_position: Optional[Decimal] = Field(default=None)
    volume_level: Optional[Decimal] = Field(default=None, ge=0.0, le=100.0)
    playback_speed: Optional[Decimal] = Field(default=None, gt=0.0)
    is_muted: Optional[bool] = Field(default=None)
    is_fullscreen: Optional[bool] = Field(default=None)


class UserPreferenceCreate(SQLModel, table=False):
    """Schema for creating user preference."""

    preference_key: str = Field(max_length=100)
    preference_value: str = Field(max_length=500)
    data_type: str = Field(max_length=20)
    description: str = Field(default="", max_length=200)


class VideoTagCreate(SQLModel, table=False):
    """Schema for creating video tag."""

    name: str = Field(max_length=100)
    color: Optional[str] = Field(default=None, max_length=7)


class VideoSearchParams(SQLModel, table=False):
    """Schema for video search parameters."""

    title: Optional[str] = Field(default=None)
    format: Optional[str] = Field(default=None)
    min_duration: Optional[Decimal] = Field(default=None)
    max_duration: Optional[Decimal] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    limit: int = Field(default=50, le=1000)
    offset: int = Field(default=0, ge=0)

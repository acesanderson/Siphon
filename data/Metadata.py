from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SiphonMetadata(BaseModel):
    """
    Base class for typing metadata objects.
    """

    pass


class FileMetadata(SiphonMetadata):
    file_path: str
    file_size: int
    mime_type: str
    file_extension: str


class YouTubeMetadata(SiphonMetadata):
    video_id: str
    channel_name: str
    duration_seconds: float
    view_count: Optional[int] = None
    upload_date: Optional[datetime] = None


class OnlineMetadata(SiphonMetadata):
    url: str
    html_title: Optional[str] = None
    content_type: Optional[str] = None  # e.g., "article", "blog", "news"


class EmailMetadata(SiphonMetadata):
    message_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    has_attachments: bool = False


class GitHubMetadata(SiphonMetadata):
    repository_name: str
    file_path_in_repo: str
    branch_name: str = "main"


class ObsidianMetadata(SiphonMetadata):
    note_path: str
    wiki_links: list[str] = []
    urls: list[str] = []
    note_type: Optional[str] = None  # "daily", "project", "person"

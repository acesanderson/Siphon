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
    content_created_at: Optional[int]
    content_modified_at: Optional[int]

    @classmethod
    def from_path(cls, filepath: "str | Path"):
        from pathlib import Path
        import mimetypes

        path = Path(filepath)
        return cls(
            file_path=str(path.resolve()),
            file_size=path.stat().st_size,
            mime_type=mimetypes.guess_type(path)[0] or "application/octet-stream",
            file_extension=path.suffix,
            content_created_at=int(path.stat().st_ctime),
            content_modified_at=int(path.stat().st_mtime),
        )
    
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

    @classmethod
    def from_github_url(cls, url: str):
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid GitHub URL format")
        
        return cls(
            repository_name=path_parts[0],
            file_path_in_repo="/".join(path_parts[1:]),
            branch_name=path_parts[2] if len(path_parts) > 2 else "main"
        )

class ObsidianMetadata(FileMetadata):
    """Inherits and mixes with FileMetadata for Obsidian-specific notes."""
    note_path: str
    wiki_links: list[str] = []
    note_type: Optional[str] = None  # "daily", "project", "person"

    @classmethod
    def _parse_obsidian_content(cls, file_path: str):
        """
        Parse Obsidian-specific content from the file.
        This is a placeholder for actual parsing logic.
        """
        # For now, we will just return an empty dict
        # In a real implementation, this would extract wiki links, note type, etc.
        # return {
        #     "note_path": file_path,
        #     "wiki_links": [],
        #     "note_type": None
        # }
        raise NotImplementedError("Obsidian content parsing not implemented yet.")

    @classmethod
    def from_obsidian_file(cls, file_path, vault_name=None):
        # Get file metadata first
        file_data = FileMetadata.from_path(file_path).dict()
        
        # Add Obsidian-specific parsing
        obsidian_data = cls._parse_obsidian_content(file_path)
        
        # Combine and create instance
        return cls(**file_data, **obsidian_data)

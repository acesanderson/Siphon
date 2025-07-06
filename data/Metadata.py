"""
Takes URI and generates the relevant Metadata object, which is a necessary part of our ProcessedContent.
"""
from Siphon.data.URI import URI
from pydantic import BaseModel, Field
from typing import Optional, Literal


class Metadata(BaseModel):
    """
    Base class for typing metadata objects as well as constructing / deserializing them.
    We have two class-level constructors here:
    - from_uri: for generating metadata from a URI string (routes to constructors in subclasses)
    - from_dict: for deserializing from a dictionary (handled within this class, returning subclass instances)
    """

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create metadata from a URI string.
        Routes to the appropriate subclass constructor based on the URI type.
        """
        match uri.source_type:
            case "youtube":
                return YouTubeMetadata.from_uri(uri)
            case "file":
                return FileMetadata.from_uri(uri)
            case "article":
                return OnlineMetadata.from_uri(uri)
            case "email":
                return EmailMetadata.from_uri(uri)
            case "github":
                return GitHubMetadata.from_uri(uri)
            case "obsidian":
                return ObsidianMetadata.from_uri(uri)
            case "drive":
                return FileMetadata.from_uri(uri)
            case _:
                raise ValueError(f"Unsupported source type: {uri.source_type}")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Deserialize from a dictionary to an instance of the appropriate subclass.
        """
        if "file_path" in data.keys():
            return FileMetadata(**data)
        elif "video_id" in data.keys():
            return YouTubeMetadata(**data)
        elif "url" in data.keys():
            return OnlineMetadata(**data)
        elif "message_id" in data.keys():
            return EmailMetadata(**data)
        elif "repository_name" in data.keys():
            return GitHubMetadata(**data)
        elif "note_path" in data.keys():
            return ObsidianMetadata(**data)
        elif "file_id" in data.keys():
            return FileMetadata(**data)


class FileMetadata(Metadata):
    file_path: str
    file_size: int
    mime_type: str
    file_extension: str
    content_created_at: Optional[int]
    content_modified_at: Optional[int]

    @classmethod
    def from_uri(cls, uri: URI):
        """Factory method to create FileMetadata from a URI object."""
        from pathlib import Path
        import mimetypes

        path = Path(uri.source)
        return cls(
            file_path=str(path.resolve()),
            file_size=path.stat().st_size,
            mime_type=mimetypes.guess_type(path)[0] or "application/octet-stream",
            file_extension=path.suffix,
            content_created_at=int(path.stat().st_ctime),
            content_modified_at=int(path.stat().st_mtime),
        )


class YouTubeMetadata(Metadata):
    video_id: str
    channel_name: str
    duration_seconds: float
    view_count: Optional[int] = None
    upload_date: Optional[int] = None

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create YouTubeMetadata from a URI object.
        Extracts video_id and channel_name from the URI.
        """
        if not uri.uri.startswith("https://www.youtube.com/watch?v="):
            raise ValueError("Invalid YouTube URI format")

        raise NotImplementedError("YouTubeMetadata parsing not implemented yet.")


class OnlineMetadata(Metadata):
    url: str
    html_title: Optional[str] = None
    content_type: Optional[str] = None  # e.g., "article", "blog", "news"

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create OnlineMetadata from a URI object.
        Extracts URL and optionally HTML title and content type.
        """
        if not uri.uri.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")

        raise NotImplementedError("OnlineMetadata parsing not implemented yet.")


class EmailMetadata(Metadata):
    message_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    has_attachments: bool = False
    received_time: Optional[int] = None  # Unix timestamp

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create EmailMetadata from a URI object.
        Extracts message_id and other email-specific fields.
        """
        if not uri.uri.startswith("email:"):
            raise ValueError("Invalid email URI format")

        raise NotImplementedError("EmailMetadata parsing not implemented yet.")


class GitHubMetadata(Metadata):
    repository_name: str
    file_path_in_repo: str
    branch_name: str = "main"

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create GitHubMetadata from a URI object.
        Extracts repository name, file path, and branch name from the URI.
        """
        from urllib.parse import urlparse

        parsed_url = urlparse(uri.source)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid GitHub URL format")

        raise NotImplementedError("GitHubMetadata parsing not implemented yet.")


class ObsidianMetadata(FileMetadata):
    """Inherits and mixes with FileMetadata for Obsidian-specific notes."""

    note_path: str
    wiki_links: list[str] = []
    urls: list[str] = []
    note_type: Literal["daily", "code_project", "organization", "topic", "generic"] = (
        "generic"
    )

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
    def from_uri(cls, uri: URI):
        """
        Factory method to create ObsidianMetadata from a URI object.
        This method first retrieves the file metadata and then parses Obsidian-specific content.
        """
        # Get file metadata first
        file_data = FileMetadata.from_uri(uri)

        # Add Obsidian-specific parsing
        obsidian_data = cls._parse_obsidian_content(uri.source)

        # Combine and create instance
        return cls(**file_data, **obsidian_data)


class DriveMetadata(Metadata):
    """
    Metadata for Google Docs files.
    """

    name: str
    description: Optional[str] = None
    mime_type: str
    created_time: Optional[int] = None
    modified_time: Optional[int] = None
    owned_by_me: bool = False
    owners: list[str] = []

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create DriveMetadata from a URI object.
        Extracts Google Drive-specific metadata.
        """
        if not uri.uri.startswith("https://docs.google.com/"):
            raise ValueError("Invalid Google Drive URI format")

        raise NotImplementedError("DriveMetadata parsing not implemented yet.")


class ToDoMetadata(Metadata):
    """
    Obsidian ToDos, as scraped when prcoessing obsidian files.
    Needs some special thinking about how to handle, resolve duplicates, etc.
    Also needs implementation of URI, ingestion, etc.
    Design backwards from my ADHD brain and how you would handle a mass of todos, some of which will never be completed.
    """

    source_file: URI = Field(..., description="URI for file to do is associated with.")
    date_created: int = Field(
        ...,
        description="Unix epoch time for when todo was first detected by scripts / last modified data for file on first scrape.",
    )
    date_completed: int = Field(
        ...,
        description="Unix epoch time for first time todo was noticed to be completed.",
    )

    @classmethod
    def from_uri(cls, uri: URI):
        _ = uri
        raise NotImplementedError("ToDos not implemented yet.")

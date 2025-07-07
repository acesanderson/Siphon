"""
Takes URI and generates the relevant Metadata object, which is a necessary part of our ProcessedContent.
"""

from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import BaseModel, Field
from typing import Optional
from time import time


class Metadata(BaseModel):
    """
    Base class for typing metadata objects as well as constructing / deserializing them.
    We have two class-level constructors here:
    - from_uri: for generating metadata from a URI string (routes to constructors in subclasses)
    - from_dict: for deserializing from a dictionary (handled within this class, returning subclass instances)
    """

    # Temporal data (as Unix timestamps)
    ingested_at: int = Field(
        default_factory=lambda: int(time()),
        description="Unix epoch time for when the metadata was created.",
    )
    last_updated_at: Optional[int] = Field(
        default=None,
        description="Unix epoch time for when the metadata was last updated.",
    )

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create metadata from a URI string.
        Routes to the appropriate subclass constructor based on the URI type.
        """
        match uri.source_type:
            case SourceType.YOUTUBE:
                from Siphon.metadata.youtube_metadata import YouTubeMetadata

                return YouTubeMetadata.from_uri(uri)
            case SourceType.FILE:
                from Siphon.metadata.file_metadata import FileMetadata

                return FileMetadata.from_uri(uri)
            case SourceType.ARTICLE:
                from Siphon.metadata.article_metadata import ArticleMetadata

                return ArticleMetadata.from_uri(uri)
            case SourceType.EMAIL:
                from Siphon.metadata.email_metadata import EmailMetadata

                return EmailMetadata.from_uri(uri)
            case SourceType.GITHUB:
                from Siphon.metadata.github_metadata import GitHubMetadata

                return GitHubMetadata.from_uri(uri)
            case SourceType.OBSIDIAN:
                from Siphon.metadata.obsidian_metadata import ObsidianMetadata

                return ObsidianMetadata.from_uri(uri)
            case SourceType.DRIVE:
                from Siphon.metadata.drive_metadata import DriveMetadata

                return DriveMetadata.from_uri(uri)
            case _:
                raise ValueError(f"Unsupported source type: {uri.source_type}")

    def __repr__(self):
        """
        Custom string representation for debugging.
        """
        # We want classname, followed by top four attributes.
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if k in self.__fields__ and v is not None
        )
        return f"{self.__class__.__name__}({attrs})"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def from_dict(cls, data: dict):
        """
        Deserialize from a dictionary to an instance of the appropriate subclass.
        """
        if "file_path" in data.keys():
            from Siphon.metadata.file_metadata import FileMetadata

            return FileMetadata(**data)
        elif "video_id" in data.keys():
            from Siphon.metadata.youtube_metadata import YouTubeMetadata

            return YouTubeMetadata(**data)
        elif "url" in data.keys():
            from Siphon.metadata.article_metadata import ArticleMetadata

            return ArticleMetadata(**data)
        elif "message_id" in data.keys():
            from Siphon.metadata.email_metadata import EmailMetadata

            return EmailMetadata(**data)
        elif "repository_name" in data.keys():
            from Siphon.metadata.github_metadata import GitHubMetadata

            return GitHubMetadata(**data)
        elif "note_path" in data.keys():
            from Siphon.metadata.obsidian_metadata import ObsidianMetadata

            return ObsidianMetadata(**data)
        elif "file_id" in data.keys():
            from Siphon.metadata.drive_metadata import DriveMetadata

            return DriveMetadata(**data)

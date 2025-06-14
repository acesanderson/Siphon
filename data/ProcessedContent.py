"""
Polymorphic base class for all processed content in Siphon system.
Each data source gets its own specialized subclass with relevant metadata.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from pathlib import Path
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import time


class ProcessedContent(BaseModel, ABC):
    """Base class for all processed content in Siphon"""

    # Universal fields for all content types
    content_id: str = Field(
        ..., description="Unique identifier (SHA-256 hash or URL-derived)"
    )
    llm_context: str = Field(..., description="LLM-ready text content")
    content_type: Literal["file", "url", "audio_recording", "email", "api_data"] = (
        Field(..., description="Type of content source")
    )

    # Optional enrichment fields
    description: str = Field(default="", description="LLM-generated description")
    summary: str = Field(
        default="", description="LLM-generated summary with provenance"
    )
    comments: str = Field(default="", description="User-provided comments")

    # Metadata
    processed_at: float = Field(
        default_factory=time.time, description="Unix timestamp of processing"
    )
    processor_version: str = Field(
        default="1.0", description="Version of Siphon that processed this"
    )

    @abstractmethod
    def get_display_name(self) -> str:
        """Return a human-readable name for this content"""
        pass


class ProcessedFile(ProcessedContent):
    """File-based content with filesystem metadata"""

    content_type: Literal["file"] = Field(default="file")

    # File-specific fields
    abs_path: str = Field(..., description="Absolute filesystem path")
    file_extension: str = Field(..., description="File extension (.pdf, .mp3, etc.)")
    file_size: int = Field(..., description="File size in bytes")
    file_modified_at: float = Field(..., description="File's last modified timestamp")

    # Processing metadata
    conversion_method: str = Field(
        ..., description="Method used (markitdown, whisper, etc.)"
    )

    def get_display_name(self) -> str:
        return Path(self.abs_path).name

    @classmethod
    def from_path(
        cls, file_path: Path, llm_context: str, conversion_method: str
    ) -> "ProcessedFile":
        """Factory method to create ProcessedFile from path"""
        import hashlib

        # Generate content_id from file hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        content_id = sha256_hash.hexdigest()

        stat = file_path.stat()

        return cls(
            content_id=content_id,
            llm_context=llm_context,
            abs_path=str(file_path.resolve()),
            file_extension=file_path.suffix.lower(),
            file_size=stat.st_size,
            file_modified_at=stat.st_mtime,
            conversion_method=conversion_method,
        )


class ProcessedURL(ProcessedContent):
    """Web-based content (articles, YouTube, etc.)"""

    content_type: Literal["url"] = Field(default="url")

    # URL-specific fields
    source_url: str = Field(..., description="Original URL")
    domain: str = Field(..., description="Domain name (youtube.com, etc.)")
    url_type: Literal["youtube", "article", "webpage", "other"] = Field(
        ..., description="Categorized URL type"
    )

    # Web-specific metadata
    title: Optional[str] = Field(
        default=None, description="Page/video title if available"
    )
    author: Optional[str] = Field(
        default=None, description="Author/channel name if available"
    )
    published_date: Optional[str] = Field(
        default=None, description="Publication date if available"
    )

    # HTTP metadata
    status_code: Optional[int] = Field(
        default=None, description="HTTP status code during fetch"
    )
    content_length: Optional[int] = Field(
        default=None, description="Content length in characters"
    )

    def get_display_name(self) -> str:
        return self.title or self.source_url

    @classmethod
    def from_url(cls, url: str, llm_context: str, **kwargs) -> "ProcessedURL":
        """Factory method to create ProcessedURL"""
        import hashlib

        # Generate content_id from URL hash
        content_id = hashlib.sha256(url.encode()).hexdigest()
        parsed = urlparse(url)

        # Determine URL type
        url_type = "other"
        if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
            url_type = "youtube"
        elif any(indicator in url.lower() for indicator in ["article", "blog", "news"]):
            url_type = "article"
        else:
            url_type = "webpage"

        return cls(
            content_id=content_id,
            llm_context=llm_context,
            source_url=url,
            domain=parsed.netloc,
            url_type=url_type,
            **kwargs,
        )


class ProcessedAudioRecording(ProcessedContent):
    """Live audio recordings with recording metadata"""

    content_type: Literal["audio_recording"] = Field(default="audio_recording")

    # Recording-specific fields
    recording_path: str = Field(..., description="Path to saved recording file")
    duration_seconds: float = Field(..., description="Recording duration")
    recording_quality: str = Field(..., description="Audio quality settings")

    # Recording session metadata
    recording_started_at: float = Field(..., description="When recording began")
    recording_location: Optional[str] = Field(
        default=None, description="Location if available"
    )
    device_info: Optional[dict[str, Any]] = Field(
        default=None, description="Recording device metadata"
    )

    # Transcription metadata
    has_speaker_diarization: bool = Field(
        default=False, description="Whether speakers were identified"
    )
    speaker_count: Optional[int] = Field(
        default=None, description="Number of identified speakers"
    )
    transcription_confidence: Optional[float] = Field(
        default=None, description="Average confidence score"
    )

    def get_display_name(self) -> str:
        from datetime import datetime

        recording_time = datetime.fromtimestamp(self.recording_started_at)
        return f"Recording_{recording_time.strftime('%Y%m%d_%H%M%S')}"


class ProcessedEmail(ProcessedContent):
    """Email content forwarded to Siphon"""

    content_type: Literal["email"] = Field(default="email")

    # Email-specific fields
    message_id: str = Field(..., description="Email message ID")
    from_address: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    received_at: float = Field(..., description="When email was received")

    # Email metadata
    has_attachments: bool = Field(
        default=False, description="Whether email had attachments"
    )
    attachment_count: int = Field(
        default=0, description="Number of attachments processed"
    )
    thread_id: Optional[str] = Field(
        default=None, description="Email thread identifier"
    )

    def get_display_name(self) -> str:
        return f"Email: {self.subject}"


class ProcessedAPIData(ProcessedContent):
    """Data from APIs, databases, or automated sources"""

    content_type: Literal["api_data"] = Field(default="api_data")

    # API-specific fields
    source_system: str = Field(
        ..., description="Source system (GitHub, Obsidian, etc.)"
    )
    api_endpoint: Optional[str] = Field(default=None, description="API endpoint used")
    data_type: str = Field(..., description="Type of data (repo, note, etc.)")

    # API metadata
    last_updated: Optional[float] = Field(
        default=None, description="When source data was last updated"
    )
    sync_method: str = Field(
        ..., description="How data was retrieved (webhook, polling, etc.)"
    )
    external_id: Optional[str] = Field(default=None, description="ID in source system")

    def get_display_name(self) -> str:
        return f"{self.source_system}: {self.data_type}"


# Factory function to create appropriate subclass
def create_processed_content(
    content_type: str, source: str, llm_context: str, **kwargs
) -> ProcessedContent:
    """Factory function to create the appropriate ProcessedContent subclass"""

    if content_type == "file":
        from pathlib import Path

        return ProcessedFile.from_path(Path(source), llm_context, **kwargs)

    elif content_type == "url":
        return ProcessedURL.from_url(source, llm_context, **kwargs)

    elif content_type == "audio_recording":
        return ProcessedAudioRecording(
            content_id=kwargs.get("content_id", ""),
            llm_context=llm_context,
            recording_path=source,
            **kwargs,
        )

    elif content_type == "email":
        return ProcessedEmail(
            content_id=kwargs.get("content_id", ""),
            llm_context=llm_context,
            message_id=source,
            **kwargs,
        )

    elif content_type == "api_data":
        return ProcessedAPIData(
            content_id=kwargs.get("content_id", ""),
            llm_context=llm_context,
            source_system=source,
            **kwargs,
        )

    else:
        raise ValueError(f"Unknown content type: {content_type}")

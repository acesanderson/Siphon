from Siphon.data.Metadata import SiphonMetadata
from Siphon.data.URI import SiphonURI
from Siphon.data.SourceType import SourceType
from Siphon.data.SyntheticData import SyntheticData
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import time


class ProcessedContent(BaseModel):
    # Primary identifiers
    content_id: str = Field(
        ..., description="Unique identifier for the content, a hash or doc ID"
    )
    uri: SiphonURI = Field(
        ..., description="Original URI of the content, used for retrieval"
    )

    # Source classification
    source_type: SourceType = Field(
        ..., description="Type of source (e.g., obsidian, file, youtube, drive, etc.)"
    )

    # Temporal data (as Unix timestamps)
    content_created_at: int
    content_modified_at: int
    ingested_at: int
    last_updated_at: int

    # Core processed data
    llm_context: str = Field(
        ..., description="Processed content ready for LLM consumption"
    )

    # Synthetic data (title, description, summary, topics, entities) -- added post init
    synthetic_data: Optional[SyntheticData] = Field(
        default=None, description="AI-generated enrichments applied to the content"
    )

    # Relationships
    related_content_ids: list[str] = Field(
        default_factory=list,
        description="List of content IDs related to this content, useful for linking and navigation.",
    )
    parent_content_id: str = Field(
        default="None",
        description="ID of the parent content if this is a part of a larger document or thread.",
    )

    # Source-specific metadata (typed)
    metadata: SiphonMetadata = Field(
        default_factory=SiphonMetadata,
        description="Source-specific metadata, such as file size, author, etc.",
    )

    @classmethod
    def create_with_current_time(cls, **kwargs):
        """Helper method to create ProcessedContent with current timestamp"""
        current_time = int(time.time())

        # Set default timestamps if not provided
        kwargs.setdefault("content_created_at", current_time)
        kwargs.setdefault("content_modified_at", current_time)
        kwargs.setdefault("ingested_at", current_time)
        kwargs.setdefault("last_updated_at", current_time)

        return cls(**kwargs)

    def get_datetime(self, field_name: str) -> datetime:
        """Convert Unix timestamp back to datetime object"""
        timestamp = getattr(self, field_name)
        return datetime.fromtimestamp(timestamp)

    def update_modified_time(self):
        """Update the last_updated_at timestamp to current time"""
        self.last_updated_at = int(time.time())

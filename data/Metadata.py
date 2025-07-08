"""
Takes URI and generates the relevant Metadata object, which is a necessary part of our ProcessedContent.
"""

from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from pydantic import BaseModel, Field
from typing import Optional
from time import time

logger = get_logger(__name__)


class Metadata(BaseModel):
    """
    Base class for typing metadata objects as well as constructing / deserializing them.
    We have two class-level constructors here:
    - from_uri: for generating metadata from a URI string (routes to constructors in subclasses)
    - from_dict: for deserializing from a dictionary (handled within this class, returning subclass instances)
    """

    sourcetype: SourceType = Field(
        ...,
        description="Type of source for the metadata, e.g., YouTube, File, Article, etc.",
    )

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
        Routes to the appropriate subclass constructor based on the sourcetype.
        """
        from Siphon.metadata.metadata_classes import MetadataClasses

        for metadata_class in MetadataClasses:
            if metadata_class.sourcetype == cls.sourcetype:
                logger.info(f"Using Metadata class: {metadata_class.__name__}")
                return metadata_class.from_uri(uri)

"""
Takes a source (string representation of file_path, url, etc.) and returns a URI object, which is necessary for our ProcessedContent and in fact our main identifier for caching.
"""

from Siphon.data.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class URI(BaseModel):
    source: str = Field(..., description="The original source URL, filepath, etc.")
    source_type: SourceType = Field(
        ..., description="The type of source this URI represents."
    )
    uri: str = Field(..., description="The URI string representation of the source.")

    @classmethod
    def identify(cls, source) -> SourceType:
        """
        Check the source string against all URI subclasses to determine SourceType.
        The overriden identify method in each subclass should return True if it can handle the source.
        """
        from Siphon.uri.uri_classes import URIClasses

        for uri_class in URIClasses:
            if uri_class.identify(source):
                return uri_class.source_type
        logger.warning(f"Unsupported source format: {source}")
        raise ValueError(f"Unsupported source format: {source}")

    @classmethod
    def from_source(cls, source: str) -> "URI | None":
        """
        Create a URI object from a source string.
        Also a validation function.
        """
        from Siphon.uri.uri_classes import URIClasses

        logger.info("Source string received.")
        source_type = cls.identify(source)
        logger.info(f"Source type determined: {source_type}")
        for uri_class in URIClasses:
            if uri_class.source_type == source_type:
                logger.info(f"Using URI class: {uri_class.__name__}")
                return uri_class.from_source(source)

    def __repr__(self) -> str:
        """Clean, informative representation showing type and processed URI"""
        return f"URI({self.source_type.value}: '{self.uri}')"

    def __str__(self) -> str:
        """String representation is just the processed URI"""
        return self.uri

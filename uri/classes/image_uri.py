from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from Siphon.data.Extensions import Extensions
from Siphon.data.URISchemes import URISchemes
from Siphon.logs.logging_config import get_logger
from pydantic import Field
from typing import override
from pathlib import Path


logger = get_logger(__name__)


class ImageURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.IMAGE,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:  # type: ignore
        """
        Check if the source string matches the text URI format.
        """
        source_path = Path(source)
        if source_path.exists():
            extension = source_path.suffix.lower()
            if extension in Extensions["Image"]:
                logger.info(f"Identified as ImageURI: {source}")
                return True
        else:
            logger.info(f"Source path does not exist: {source}")
            return False

    @override
    @classmethod
    def from_source(cls, source: str) -> "ImageURI | None":  # type: ignore
        """
        Create an ImageURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match ImageURI format: {source}")
            return None
        return cls(
            source=source,
            uri=f"{URISchemes['Image']}://{Path(source).as_posix()}",
        )

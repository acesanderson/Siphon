from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from Siphon.data.types.Extensions import Extensions
from Siphon.data.types.URISchemes import URISchemes
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
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the image URI format.
        """
        try:
            if "http" in source or "https" in source:
                logger.info(f"This is a URL, not an ImageURI: {source}")
                return False
            source_path = Path(source)
            extension = source_path.suffix.lower()
            if extension in Extensions["Image"]:
                logger.info(f"Identified as ImageURI: {source}")
                return True
            return False
        except Exception:
            return False

    @override
    @classmethod
    def from_source(cls, source: str, skip_checksum: bool = False) -> "ImageURI | None":
        """
        Create an ImageURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match ImageURI format: {source}")
            return None

        # Coerce to Path if a string is provided
        source_path = Path(source) if isinstance(source, str) else source_path

        # Calculate checksum
        checksum = None
        if not skip_checksum:
            logger.info(f"Calculating checksum for: {source_path}")
            checksum = cls.get_checksum(source_path)
            logger.info(f"Checksum calculated: {checksum}")

        # Always convert to absolute path for consistency
        absolute_source = str(Path(source).resolve())

        return cls(
            source=absolute_source,
            uri=f"{URISchemes['Image']}://{Path(absolute_source).as_posix()}",
            checksum=checksum,
        )

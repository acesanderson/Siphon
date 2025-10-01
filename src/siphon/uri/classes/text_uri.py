from siphon.data.uri import URI
from siphon.data.type_definitions.source_type import SourceType
from siphon.logs.logging_config import get_logger
from siphon.data.type_definitions.uri_schemes import URISchemes
from siphon.data.type_definitions.extensions import Extensions
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class TextURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    Includes a hash as an additional cache key. (since we may have multiple files with the same name across different directories of hosts.)
    """

    sourcetype: SourceType = Field(
        default=SourceType.TEXT,
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the text URI format.
        No file access required - just check the extension.
        """
        try:
            if "http" in source or "https" in source:
                logger.info(f"This is a URL, not an TextURI: {source}")
                return False
            source_path = Path(source)
            extension = source_path.suffix.lower()
            if extension in Extensions["Text"]:
                logger.info(f"Identified as TextURI: {source}")
                return True
            return False
        except Exception:
            return False

    @override
    @classmethod
    def from_source(cls, source: str, skip_checksum: bool = False) -> "TextURI | None":
        """
        Create a TextURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match TextURI format: {source}")
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

        logger.info(f"Creating File URI object for: {absolute_source}")

        return cls(
            source=absolute_source,
            uri=f"{URISchemes['Text']}://{Path(absolute_source).as_posix()}",
            checksum=checksum,
        )

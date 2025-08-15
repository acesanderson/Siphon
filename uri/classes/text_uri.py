from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from Siphon.data.types.URISchemes import URISchemes
from Siphon.data.types.Extensions import Extensions
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class TextURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
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
    def from_source(cls, source: str) -> "TextURI | None":
        """
        Create a TextURI object from a source string.
        No file access required.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match TextURI format: {source}")
            return None

        # Always convert to absolute path for consistency
        absolute_source = str(Path(source).resolve())

        return cls(
            source=absolute_source,
            uri=f"{URISchemes['Text']}://{Path(absolute_source).as_posix()}",
        )

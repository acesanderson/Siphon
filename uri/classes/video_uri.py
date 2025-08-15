from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from Siphon.data.types.Extensions import Extensions
from Siphon.data.types.URISchemes import URISchemes
from Siphon.logs.logging_config import get_logger
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class VideoURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.VIDEO,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the video URI format.
        """
        try:
            source_path = Path(source)
            extension = source_path.suffix.lower()
            if extension in Extensions["Video"]:
                logger.info(f"Identified as VideoURI: {source}")
                return True
            return False
        except Exception:
            return False

    @override
    @classmethod
    def from_source(cls, source: str) -> "VideoURI | None":
        """
        Create a VideoURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match VideoURI format: {source}")
            return None

        # Always convert to absolute path for consistency
        absolute_source = str(Path(source).resolve())

        return cls(
            source=absolute_source,
            sourcetype=SourceType.VIDEO,
            uri=f"{URISchemes['Video']}://{Path(absolute_source).as_posix()}",
        )

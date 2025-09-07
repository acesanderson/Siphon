from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from Siphon.data.types.Extensions import Extensions
from Siphon.data.types.URISchemes import URISchemes
from Siphon.logs.logging_config import get_logger
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class AudioURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.AUDIO,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the audio URI format.
        """
        try:
            source_path = Path(source)
            extension = source_path.suffix.lower()
            if extension in Extensions["Audio"]:
                logger.info(f"Identified as AudioURI: {source}")
                return True
            return False
        except Exception:
            return False

    @override
    @classmethod
    def from_source(cls, source: str) -> "AudioURI | None":
        """
        Create an AudioURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match AudioURI format: {source}")
            return None

        # Coerce to Path if a string is provided
        source_path = Path(source) if isinstance(source, str) else source_path

        # Calculate checksum
        logger.info(f"Calculating checksum for: {source_path}")
        checksum = cls.get_checksum(source_path)
        logger.info(f"Checksum calculated: {checksum}")

        # Always convert to absolute path for consistency
        absolute_source = str(Path(source).resolve())

        return cls(
            source=absolute_source,
            uri=f"{URISchemes['Audio']}://{Path(absolute_source).as_posix()}",
        )

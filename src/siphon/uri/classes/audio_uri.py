from siphon.data.uri import URI
from siphon.data.type_definitions.source_type import SourceType
from siphon.data.type_definitions.extensions import Extensions
from siphon.data.type_definitions.uri_schemes import URISchemes
from siphon.logs.logging_config import get_logger
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
            if "http" in source or "https" in source:
                logger.info(f"This is a URL, not an AudioURI: {source}")
                return False
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
    def from_source(cls, source: str, skip_checksum: bool = False) -> "AudioURI | None":
        """
        Create an AudioURI object from a source string.
        """
        if not cls.identify(source):
            logger.warning(f"Source does not match AudioURI format: {source}")
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
            uri=f"{URISchemes['Audio']}://{Path(absolute_source).as_posix()}",
            checksum=checksum,
        )

from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from Siphon.data.types.URISchemes import URISchemes
from Siphon.data.types.Extensions import Extensions
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class EphemeralURI(URI):
    """
    Represents ephemeral data, like stdin, clipboard, or other non-persistent sources.
    """

    sourcetype: SourceType = Field(
        default=SourceType.EPHEMERAL,
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Ephemeral flips our usual approach; URI comes AFTER the context.
        """
        raise NotImplementedError("EphemeralURI cannot identify from a source string.")

    @classmethod
    def from_content(cls, content: str, content_type: str) -> "EphemeralURI":
        """
        Create an EphemeralURI object from content string. This is the opposite of the usual URI creation process.
        """
        import hashlib
        import time

        # Content hash for uniqueness and cache consistency
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]

        # Timestamp for temporal uniqueness (same content at different times)
        timestamp = int(time.time())

        # Combine for unique identifier
        unique_identifier = f"{content_type}/{timestamp}-{content_hash}"

        return cls(
            source=f"ephemeral://{unique_identifier}",
            uri=f"{URISchemes['Ephemeral']}://{unique_identifier}",
        )

    @override
    @classmethod
    def from_source(cls, source: str, skip_checksum: bool = False):
        """
        Not implemented, this is purely an inherited method.
        """
        raise NotImplementedError(
            "Ephemeral content cannot be created from a source string."
        )

"""
Takes a source (string representation of file_path, url, etc.) and returns a URI object, which is necessary for our ProcessedContent and in fact our main identifier for caching.
Two essential artifacts are created here:
- the URI (which is main identifier)
- the SourceType (which routes our pipeline from e2e)
"""

from functools import lru_cache
from Siphon.data.types.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path

logger = get_logger(__name__)


class URI(BaseModel):
    source: str = Field(..., description="The original source URL, filepath, etc.")
    sourcetype: SourceType = Field(
        ..., description="The type of source this URI represents."
    )
    uri: str = Field(..., description="The URI string representation of the source.")

    # For files, we can store a checksum to verify integrity
    checksum: str | None = Field(
        default=None,
        description="Checksum of the text file for integrity verification.",
    )

    @classmethod
    def identify(cls, source: str) -> bool: ...  # type: ignore

    @classmethod
    @lru_cache(maxsize=1000)
    def from_source(cls, source: str | Path) -> Optional["URI"]:
        """
        Create a URI object from a source string.
        Tries each URI subclass until one can handle the source.
        """
        from Siphon.uri.uri_classes import URIClasses

        logger.info("Source string received.")

        if isinstance(source, Path):
            source = str(source)

        # Try each URI class to see if it can handle this source
        for uri_class in URIClasses:
            if uri_class.identify(source):  # Each subclass has its own identify method
                logger.info(f"Using URI class: {uri_class.__name__}")
                return uri_class.from_source(source)

        # No class could handle this source
        logger.warning(f"Unsupported source format: {source}")
        return None

    @classmethod
    def get_checksum(cls, file_path: str | Path) -> str:
        """
        Calculate the checksum of a file using the specified algorithm.
        """
        # Coerce to Path if a string is provided
        file_path = Path(file_path) if isinstance(file_path, str) else file_path

        # Ensure the file exists and is not empty
        assert file_path.is_file(), f"File does not exist: {file_path}"
        assert file_path.stat().st_size > 0, f"File is empty: {file_path}"

        # Calculate checksum
        import hashlib

        h = hashlib.new("sha256")
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):  # read in chunks
                h.update(chunk)
        assert h.hexdigest(), "Checksum calculation failed."
        return h.hexdigest()

    def __repr__(self) -> str:
        """Clean, informative representation showing type and processed URI"""
        return f"URI({self.sourcetype.value}: '{self.uri}')"

    def __str__(self) -> str:
        """String representation is just the processed URI"""
        return self.uri

    def __hash__(self) -> int:
        """Make URI hashable for caching purposes"""
        return hash((self.uri, self.sourcetype))

    def __eq__(self, other) -> bool:
        """Define equality for hashing"""
        if isinstance(other, URI):
            return self.uri == other.uri and self.sourcetype == other.sourcetype
        return False

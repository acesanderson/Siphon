from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from Siphon.logs.logging_config import get_logger
from Siphon.data.URISchemes import URISchemes
from Siphon.data.Extensions import Extensions
from pydantic import Field
from typing import override
from pathlib import Path

logger = get_logger(__name__)


class DocURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.DOC,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the doc URI format.
        """

        try:
            source_path = Path(source)
            if source_path.exists():
                extension = source_path.suffix.lower()
                if extension in Extensions["Doc"]:
                    logger.info(f"Identified as DocURI: {source}")
                    return True
            else:
                logger.info(f"Source path does not exist: {source}")
                return False
        except:
            pass
        return False

    @override
    @classmethod
    def from_source(cls, source: str) -> "DocURI | None":  # type: ignore
        """
        Create an DocURI object from a source string.
        """

        if not cls.identify(source):
            logger.warning(f"Source does not match DocURI format: {source}")
            return None
        return cls(
            source=source,
            uri=f"{URISchemes['Doc']}://{Path(source).as_posix()}",
        )

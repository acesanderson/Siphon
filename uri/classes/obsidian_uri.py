from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType
from pydantic import Field
from typing import override


class ObsidianURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.OBSIDIAN,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool: ...

    @override
    @classmethod
    def from_source(cls, source: str) -> "ObsidianURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        ...

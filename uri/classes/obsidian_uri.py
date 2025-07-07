from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import Field


class ObsidianURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    source_type: SourceType = Field(
        default=SourceType.OBSIDIAN,
        description="The type of source this URI represents.",
    )

    @classmethod
    def identify(cls, source: str) -> bool: ...

    @classmethod
    def from_source(cls, source: str) -> "ObsidianURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        ...

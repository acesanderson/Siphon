from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import Field
from typing import override


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
    def identify(cls, source: str) -> bool: ...

    @override
    @classmethod
    def from_source(cls, source: str) -> "AudioURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        ...

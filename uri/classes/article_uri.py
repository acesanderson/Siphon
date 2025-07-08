from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import Field
from typing import override


class ArticleURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.ARTICLE,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool: ...

    @override
    @classmethod
    def from_source(cls, source: str) -> "ArticleURI":
        """
        Create an ArticleURI object from a source string.
        """
        ...

    @classmethod
    def _parse_article_url(cls, url: str) -> tuple[str, SourceType, str]:
        """
        Parse generic article URLs
        """
        # For articles, the URI is just the original URL
        return url, SourceType.ARTICLE, url

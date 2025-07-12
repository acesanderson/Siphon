from Siphon.data.Metadata import Metadata
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import Optional, override


class ArticleMetadata(Metadata):
    """
    This is the exemplar for online resources.
    All online resources (Drive, GitHub, YouTube, Article) should have url, domain, title, and pub date.
    """
    sourcetype: SourceType = SourceType.ARTICLE
    url: str
    domain: str
    title: Optional[str] = None
    published_date: Optional[int] = None

    @override
    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create ArticleMetadata from a URI object.
        Extracts URL and optionally HTML title and content type.
        """
        if not uri.uri.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")

        raise NotImplementedError("ArticleMetadata parsing not implemented yet.")

from Siphon.data.Metadata import Metadata
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import Optional, override


class ArticleMetadata(Metadata):
    sourcetype: SourceType = SourceType.ARTICLE
    url: str
    html_title: Optional[str] = None

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

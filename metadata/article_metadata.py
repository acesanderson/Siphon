from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from typing import Optional


class ArticleMetadata(Metadata):
    url: str
    html_title: Optional[str] = None

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create ArticleMetadata from a URI object.
        Extracts URL and optionally HTML title and content type.
        """
        if not uri.uri.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")

        raise NotImplementedError("ArticleMetadata parsing not implemented yet.")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...

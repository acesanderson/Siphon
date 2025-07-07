from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from typing import Optional


class DriveMetadata(Metadata):
    """
    Metadata for Google Docs files.
    """

    name: str
    description: Optional[str] = None
    mime_type: str
    created_time: Optional[int] = None
    modified_time: Optional[int] = None
    owned_by_me: bool = False
    owners: list[str] = []

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create DriveMetadata from a URI object.
        Extracts Google Drive-specific metadata.
        """
        if not uri.uri.startswith("https://docs.google.com/"):
            raise ValueError("Invalid Google Drive URI format")

        raise NotImplementedError("DriveMetadata parsing not implemented yet.")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...

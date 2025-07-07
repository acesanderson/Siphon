from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from typing import Optional


class EmailMetadata(Metadata):
    message_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    has_attachments: bool = False
    received_time: Optional[int] = None  # Unix timestamp

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create EmailMetadata from a URI object.
        Extracts message_id and other email-specific fields.
        """
        if not uri.uri.startswith("email:"):
            raise ValueError("Invalid email URI format")

        raise NotImplementedError("EmailMetadata parsing not implemented yet.")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...

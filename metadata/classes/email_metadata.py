from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from typing import Optional, override


class EmailMetadata(Metadata):
    sourcetype: SourceType = SourceType.EMAIL

    message_id: str
    from_address: str
    to_addresses: list[str]
    subject: str
    has_attachments: bool = False
    received_time: Optional[int] = None  # Unix timestamp

    @override
    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create EmailMetadata from a URI object.
        Extracts message_id and other email-specific fields.
        """
        if not uri.uri.startswith("email:"):
            raise ValueError("Invalid email URI format")

        raise NotImplementedError("EmailMetadata parsing not implemented yet.")

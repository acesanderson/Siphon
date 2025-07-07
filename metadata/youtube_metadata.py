from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from typing import Optional


class YouTubeMetadata(Metadata):
    video_id: str
    channel_name: str
    duration_seconds: float
    view_count: Optional[int] = None
    upload_date: Optional[int] = None

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create YouTubeMetadata from a URI object.
        Extracts video_id and channel_name from the URI.
        """
        if not uri.uri.startswith("https://www.youtube.com/watch?v="):
            raise ValueError("Invalid YouTube URI format")

        raise NotImplementedError("YouTubeMetadata parsing not implemented yet.")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...

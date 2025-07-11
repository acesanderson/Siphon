from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from Siphon.data.URISchemes import URISchemes
from pydantic import Field
from urllib.parse import urlparse, parse_qs
import re


from typing import override


class YouTubeURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.YOUTUBE,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        return "youtube.com" in source or "youtu.be" in source

    @override
    @classmethod
    def from_source(cls, source: str) -> "YouTubeURI | None":  # type: ignore
        """
        Create an YouTube object from a source string.
        """
        # Handle different YouTube URL formats:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://youtube.com/watch?v=VIDEO_ID&t=123
        if "youtu.be/" in source:
            # Short format: https://youtu.be/VIDEO_ID
            video_id = source.split("youtu.be/")[1].split("?")[0].split("&")[0]
        else:
            # Long format: extract from query parameter
            parsed = urlparse(source)
            query_params = parse_qs(parsed.query)

            if "v" not in query_params:
                raise ValueError(f"Cannot find video ID in YouTube URL: {source}")

            video_id = query_params["v"][0]

        # Validate video ID format (11 characters, alphanumeric + - and _)
        if not re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
            raise ValueError(f"Invalid YouTube video ID format: {video_id}")

        uri = f"{URISchemes["YouTube"]}://{video_id}"
        return cls(
            source=source,
            uri=uri,
        )

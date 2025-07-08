from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import Field
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
        ...

        # def is_youtube_url(url: str) -> bool:
        #     return "youtube.com" in url or "youtu.be" in url
        #

    @override
    @classmethod
    def from_source(cls, source: str) -> "YouTubeURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        ...

    @classmethod
    def _parse_youtube_url(cls, url: str) -> tuple[str, SourceType, str]:
        """
        Parse YouTube URLs - Fix 4: Extract video ID properly
        """

        # Handle different YouTube URL formats:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://youtube.com/watch?v=VIDEO_ID&t=123

        if "youtu.be/" in url:
            # Short format: https://youtu.be/VIDEO_ID
            video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        else:
            # Long format: extract from query parameter
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)

            if "v" not in query_params:
                raise ValueError(f"Cannot find video ID in YouTube URL: {url}")

            video_id = query_params["v"][0]

        # Validate video ID format (11 characters, alphanumeric + - and _)
        if not re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
            raise ValueError(f"Invalid YouTube video ID format: {video_id}")

        uri = f"youtube://{video_id}"
        return url, SourceType.YOUTUBE, uri

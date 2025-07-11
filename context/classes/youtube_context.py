from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class YouTubeContext(Context):
    sourcetype: SourceType = SourceType.YOUTUBE

    @override
    @classmethod
    def from_uri(cls, uri: "YouTubeURI") -> "YouTubeContext":  # type: ignore
        """
        Create a YouTubeContext from a URI.
        """
        from Siphon.uri.classes.youtube_uri import YouTubeURI

        if not isinstance(uri, YouTubeURI):
            raise TypeError("Expected uri to be an instance of YouTubeURI.")

        raise NotImplementedError("YouTubeContext.from_uri is not implemented yet")

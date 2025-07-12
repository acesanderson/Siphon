from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class VideoContext(Context):
    sourcetype: SourceType = SourceType.VIDEO

    @override
    @classmethod
    def from_uri(cls, uri: "VideoURI") -> "VideoContext":  # type: ignore
        """
        Create a VideoContext from a URI.
        """
        from Siphon.uri.classes.video_uri import VideoURI

        if not isinstance(uri, VideoURI):
            raise TypeError("Expected uri to be an instance of VideoURI.")

        raise NotImplementedError("VideoContext.from_uri is not implemented yet")

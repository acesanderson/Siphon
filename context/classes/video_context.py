from Siphon.context.classes.text_context import TextContext
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class VideoContext(TextContext):
    """
    Context class for handling video files.
    Inherits from TextContext to provide common functionality; from_uri, _validate_uri, and _get_metadata work under the hood.
    """
    sourcetype: SourceType = SourceType.VIDEO

    @override
    @classmethod
    def _get_context(cls, uri: URI, model: str = "cloud") -> str:
        """
        Get the context from the video file.
        This method is overridden to provide specific functionality for video files.
        """
        _, _ = uri, model
        raise NotImplementedError("VideoContext._get_context is not implemented yet")


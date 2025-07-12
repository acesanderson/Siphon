from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
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

        from Siphon.ingestion.youtube.retrieve_youtube import retrieve_youtube

        llm_context = retrieve_youtube(uri.source)

        assert isinstance(llm_context, str) and len(llm_context) > 0, "Expected llm_context to be a non-empty string."

        return cls(
            context = llm_context,
        )

from Siphon.context.classes.article_context import ArticleContext
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override

class YouTubeContext(ArticleContext):
    sourcetype: SourceType = SourceType.YOUTUBE

    # Youtube specific metadata fields
    video_id: str
    channel: str
    duration: int
    view_count: int
    description: str
    tags: list[str]
    like_count: int
    comment_count: int

    @override
    @classmethod
    def _get_context(cls, uri: URI) -> tuple[str, dict]:
        """
        Get the text content + metadata from the YouTube video.
        """
        from Siphon.ingestion.youtube.retrieve_youtube import retrieve_youtube

        llm_context, metadata = retrieve_youtube(uri.source)
        return llm_context, metadata


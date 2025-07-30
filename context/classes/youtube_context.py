from Siphon.context.classes.article_context import ArticleContext
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override, Optional


class YouTubeContext(ArticleContext):
    sourcetype: SourceType = SourceType.YOUTUBE

    # Youtube specific metadata fields
    video_id: Optional[str]
    channel: Optional[str]
    duration: Optional[int]
    view_count: Optional[int]
    description: Optional[str]
    tags: Optional[list[str]]
    like_count: Optional[int]
    comment_count: Optional[int]

    @override
    @classmethod
    def _get_context(cls, uri: URI) -> tuple[str, dict]:
        """
        Get the text content + metadata from the YouTube video.
        """
        from Siphon.ingestion.youtube.retrieve_youtube import retrieve_youtube

        llm_context, metadata = retrieve_youtube(uri.source)
        return llm_context, metadata

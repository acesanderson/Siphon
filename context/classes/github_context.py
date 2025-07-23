from Siphon.context.classes.article_context import ArticleContext
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override, Optional


class GitHubContext(ArticleContext):
    """
    Context class for handling GitHub articles.
    Inherits from ArticleContext to handle GitHub-specific content.
    """

    sourcetype: SourceType = SourceType.GITHUB

    # GitHub specific metadata fields
    stars: int
    language: str
    topics: list[str]
    description: Optional[str]
    updated_at: int
    pushed_at: int
    size: int

    @override
    @classmethod
    def _get_context(cls, uri: URI) -> tuple[str, dict]:
        """
        Get the text content + metadata from the GitHub article.
        """
        from Siphon.ingestion.github.retrieve_github import retrieve_github

        llm_context, metadata = retrieve_github(uri.source)
        return llm_context, metadata

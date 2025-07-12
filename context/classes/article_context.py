from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from typing import override


class ArticleContext(Context):
    sourcetype: SourceType = SourceType.ARTICLE

    @override
    @classmethod
    def from_uri(cls, uri: "ArticleURI") -> "ArticleContext":  # type: ignore
        """
        Create a ArticleContext from a URI.
        """
        from Siphon.uri.classes.article_uri import ArticleURI

        if not isinstance(uri, ArticleURI):
            raise TypeError("Expected uri to be an instance of ImageURI.")

        from Siphon.ingestion.article.retrieve_article import retrieve_article
        llm_context = retrieve_article(uri.source)

        assert isinstance(llm_context, str) and len(llm_context) > 0, "Expected llm_context to be a non-empty string."

        return cls(
            context=llm_context,
        )

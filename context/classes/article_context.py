from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
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

        raise NotImplementedError(
            "ArticleContext.from_uri is not implemented yet. Please implement this method in your subclass."
        )

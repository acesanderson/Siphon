from siphon.data.context import Context
from siphon.data.types.source_type import SourceType
from siphon.data.uri import URI
from typing import override, Optional
import re

url_pattern = re.compile(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$")


class ArticleContext(Context):
    """
    Context class for handling articles.
    This is also the base class for other online content contexts (YouTube, GitHub, etc.).
    """

    sourcetype: SourceType = SourceType.ARTICLE

    # Metadata fields
    url: Optional[str] = None
    domain: Optional[str] = None
    title: Optional[str] = None
    published_date: Optional[int] = None

    @override
    @classmethod
    def from_uri(cls, uri: URI) -> Context:  # type: ignore
        """
        Create a ArticleContext from a URI.
        This is also the base class for other online content contexts.
        Unlike our file-based contexts, get_context returns both the context and metadata.
        This is because api calls provide both the context and metadata in one go.
        """
        if not cls._validate_uri(uri):
            raise ValueError("Invalid URI provided.")

        # Get context + metadata from the URI
        context, metadata = cls._get_context(uri)

        # Assemble and return the Context instance
        return cls(context=context, **metadata)

    @classmethod
    def _validate_uri(cls, uri: URI) -> bool:
        """
        Validate that we received the correct subclass of URI and that the file exists.
        Inheritable by other file-based contexts like AudioContext, ImageContext, etc.
        """
        if not uri.source:
            raise ValueError("URI source cannot be empty.")
        if not isinstance(uri.source, str):
            raise TypeError("URI source must be a string object.")

        # Assert that uri class name matches the expected format
        sourcetype_value = uri.sourcetype.value
        if uri.__class__.__name__ != f"{sourcetype_value}URI":
            raise TypeError(
                f"Expected uri to be an instance of {sourcetype_value}URI, "
                f"but got {uri.__class__.__name__}."
            )

        # Validate that source is a proper URL
        if not url_pattern.match(uri.source):
            raise ValueError("URI source must be a valid URL.")

        return True

    @classmethod
    def _get_context(cls, uri: URI) -> tuple[str, dict]:
        """
        Get the text content + metadata from the article.
        The most customized method for each context type (GitHub, YouTube, Drive, etc.)
        """

        from siphon.ingestion.article.retrieve_article import retrieve_article

        article_obj = retrieve_article(uri.source)
        # Get context
        context = article_obj.text
        # Get metadata
        metadata = {
            "url": article_obj.source_url,
            "domain": article_obj.source_url.split("/")[2],
            "title": article_obj.title,
            "published_date": int(article_obj.publish_date.timestamp())
            if article_obj.publish_date
            else None,  # type: ignore
        }
        return context, metadata

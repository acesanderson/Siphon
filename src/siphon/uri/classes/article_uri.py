from siphon.data.uri import URI
from siphon.data.type_definitions.source_type import SourceType
from siphon.data.type_definitions.uri_schemes import URISchemes
from siphon.logs.logging_config import get_logger
from pydantic import Field
from typing import override
import re

logger = get_logger(__name__)


class ArticleURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.ARTICLE,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        "Article" type is a catchall for any generic article URL.
        We just want to validate that the source is a URL, and that it is not:
        - github
        - youtube
        - drive
        """
        is_url_regex = re.compile(r"^(https?://)?([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$")
        is_article = re.compile(r"^(?!.*(github|youtube|drive)).*$", re.IGNORECASE)
        if is_url_regex.match(source) and is_article.match(source):
            return True

    @override
    @classmethod
    def from_source(cls, source: str, skip_checksum: bool = False) -> "ArticleURI":  # type: ignore
        """
        Create an ArticleURI object from a source string.
        """
        _ = skip_checksum  # currently unused
        if not cls.identify(source):
            raise ValueError(f"Source does not match ArticleURI format: {source}")
        return cls(
            source=source,
            uri=f"{URISchemes['Article']}://{source}",
        )

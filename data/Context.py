from pydantic import BaseModel, Field
from functools import lru_cache
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from Siphon.logs.logging_config import get_logger

logger = get_logger(__name__)


class Context(BaseModel):
    """
    LLM context generated from the URI.
    Only one attribute, context -- but this class hides the vast majority of logic in this project.
    """

    sourcetype: SourceType = Field(
        ...,
        description="Type of source for the metadata, e.g., YouTube, File, Article, etc.",
    )
    context: str = Field(..., description="The context string generated from the URI.")

    @classmethod
    @lru_cache(maxsize=1000)
    def from_uri(cls, uri: URI) -> "Context":
        """
        Create a Context object from a URI object.
        Subclasses for each SourceType override this; they return a context string.
        """
        from Siphon.context.context_classes import ContextClasses

        for context_class in ContextClasses:
            if context_class.source_type == cls.sourcetype:
                logger.info(f"Using URI class: {context_class.__name__}")
                return context_class.from_uri(uri)

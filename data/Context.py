from pydantic import BaseModel, Field
from functools import lru_cache
from Siphon.data.types.SourceType import SourceType
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
    def from_uri(cls, uri: URI) -> "Context":  # type: ignore
        """
        Create a Context object from a URI object.
        Subclasses for each SourceType override this; they return a context string.
        """
        from Siphon.context.context_classes import ContextClasses

        logger.info(f"Looking for context class for sourcetype: {uri.sourcetype.value}")

        # Calculate this from the class name minus "Context"
        for context_class in ContextClasses:
            logger.info(
                f"Checking class: {context_class.__name__} against {uri.sourcetype.value}"
            )
            if context_class.__name__.replace("Context", "") == uri.sourcetype.value:
                logger.info(f"Using URI class: {context_class.__name__}")
                return context_class.from_uri(uri)

        raise ValueError(f"No Context class found for source type {uri.sourcetype}.")

    def __hash__(self) -> int:
        """Make Context hashable for caching purposes"""
        return hash((self.context, self.sourcetype))

    def __eq__(self, other) -> bool:
        """Define equality for hashing"""
        if isinstance(other, Context):
            return self.context == other.context and self.sourcetype == other.sourcetype
        return False

from pydantic import BaseModel, Field
from functools import lru_cache
from Siphon.data.SourceType import SourceType
from Siphon.data.Context import Context
from Siphon.logs.logging_config import get_logger

logger = get_logger(__name__)


class SyntheticData(BaseModel):
    """
    AI-generated enrichments, applied as a "finishing step" to the content.
    """

    sourcetype: SourceType

    title: str = Field(
        default="", description="Title of the content, either extracted or generated"
    )
    description: str = Field(
        default="", description="Short description or summary of the content"
    )
    summary: str = Field(default="", description="Detailed summary of the content")
    topics: list[str] = Field(
        default_factory=list,
        description="List of topics or keywords associated with the content, an area liable to change with cluster analyses.",
    )
    entities: list[str] = Field(
        default_factory=list,
        description="List of entities (people, places, organizations) mentioned in the content.",
    )

    @classmethod
    @lru_cache(maxsize=1000)
    def from_context(cls, context: Context) -> "SyntheticData":
        """
        Create an instance of SyntheticData from llm context, typically generated by an LLM.
        Subclasses for each SourceType may override this.
        """
        from Siphon.synthetic_data.synthetic_data_classes import SyntheticDataClasses

        stem = context.__class__.__name__.replace("Context", "").lower()

        for synthetic_data_class in SyntheticDataClasses:
            if (
                synthetic_data_class.__name__.replace("SyntheticData", "").lower()
                == stem
            ):
                logger.info(f"Using URI class: {synthetic_data_class.__name__}")
                return synthetic_data_class.from_context(context)
        raise ValueError(f"No SyntheticData class found for context type {stem}.")

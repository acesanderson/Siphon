"""
ProcessedContent is our final output format for content processed by Siphon.
It combines our URI, LLM context, and synthetic data into a structured format, for storage / caching / retrieval from postgres.
Our CLI also has a nice display method (.pretty_print()), which we add as a mixin to this class.
"""

from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.Context import Context
from Siphon.data.types.SourceType import SourceType
from Siphon.data.ProcessedContentDisplay import ProcessedContentDisplayMixin
from pydantic import BaseModel, Field
from typing import Optional, Any


class ProcessedContent(BaseModel, ProcessedContentDisplayMixin):
    # Primary identifiers
    uri: URI = Field(..., description="Original URI of the content, used for retrieval")

    # AI context for LLM consumption
    llm_context: Context = Field(
        ..., description="Processed content + metadata ready for LLM consumption"
    )

    # Synthetic data (title, description, summary, topics, entities) -- added post init
    synthetic_data: Optional[SyntheticData] = Field(
        ..., description="AI-generated enrichments applied to the content"
    )

    tags: list[str] = Field(
        default_factory=list,
        description="List of user-generated and auto-generated tags applied to the content for categorization",
    )

    @property
    def context(self) -> str:
        """
        Full context text.
        """
        return self.llm_context.context

    @property
    def title(self) -> str:
        """Title of the content, derived from synthetic data if available."""
        return self.synthetic_data.title if self.synthetic_data else ""

    @property
    def description(self) -> str:
        """Title of the content, derived from synthetic data if available."""
        return self.synthetic_data.description if self.synthetic_data else ""

    @property
    def summary(self) -> str:
        """Summary of the content, derived from synthetic data if available."""
        return self.synthetic_data.summary if self.synthetic_data else ""

    @property
    def id(self) -> str:
        """Unique identifier for this processed content, derived from URI."""
        return self.uri.uri

    def model_dump_for_cache(self) -> dict[str, Any]:
        """Simplified serialization for caching - stores inputs to factories."""
        return {
            # Store the raw source - we can reconstruct URI from this
            "source": self.uri.source,
            "sourcetype": self.uri.sourcetype.value,
            # Store context data + type info
            "context_data": self.llm_context.model_dump(),
            # Store synthetic data
            "synthetic_data": self.synthetic_data.model_dump()
            if self.synthetic_data
            else None,
            # Store tags
            "tags": self.tags,
        }

    @classmethod
    def model_validate_from_cache(cls, data: dict[str, Any]) -> "ProcessedContent":
        """Reconstruct ProcessedContent using your existing factories."""

        # 1. Reconstruct URI using your existing from_source method
        uri = URI.from_source(data["source"])
        if not uri:
            raise ValueError(f"Could not reconstruct URI from source: {data['source']}")

        # 2. Reconstruct Context using your existing class loading
        from Siphon.context.context_classes import ContextClasses

        sourcetype = SourceType(data["sourcetype"])
        context_class = None

        for cls_candidate in ContextClasses:
            if cls_candidate.__name__.replace("Context", "") == sourcetype.value:
                context_class = cls_candidate
                break

        if not context_class:
            # Fallback to base Context class
            context_class = Context

        # Reconstruct context with stored data
        llm_context = context_class.model_validate(data["context_data"])

        # 3. Reconstruct SyntheticData
        synthetic_data = None
        if data.get("synthetic_data"):
            synthetic_data = SyntheticData.model_validate(data["synthetic_data"])

        return cls(
            uri=uri,
            llm_context=llm_context,
            synthetic_data=synthetic_data,
            tags=data.get("tags", []),
        )

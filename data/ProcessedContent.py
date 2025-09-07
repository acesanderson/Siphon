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
from typing import Optional, Any, override
import time

count = 0


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

    # Timestamps created on creation and update
    created_at: int = Field(
        default_factory=lambda: int(time.time()),
        description="Unix epoch timestamp when content was created",
    )
    updated_at: int = Field(
        default_factory=lambda: int(time.time()),
        description="Unix epoch timestamp when content was last updated",
    )

    @override
    def model_post_init(self, __context: Any) -> None:
        """
        Validate that all component classes match the declared sourcetype.
        """
        expected_sourcetype = self.uri.sourcetype

        # Check URI class matches sourcetype
        expected_uri_class = f"{expected_sourcetype.value}URI"
        actual_uri_class = self.uri.__class__.__name__
        if expected_uri_class != actual_uri_class:
            raise ValueError(
                f"URI class mismatch for {expected_sourcetype.value}: "
                f"expected {expected_uri_class}, got {actual_uri_class}"
            )

        # Check Context class matches sourcetype
        expected_context_class = f"{expected_sourcetype.value}Context"
        actual_context_class = self.llm_context.__class__.__name__
        if expected_context_class != actual_context_class:
            raise ValueError(
                f"Context class mismatch for {expected_sourcetype.value}: "
                f"expected {expected_context_class}, got {actual_context_class}"
            )

        # Only check sourcetype fields if they exist
        if (
            hasattr(self.llm_context, "sourcetype")
            and self.llm_context.sourcetype != expected_sourcetype
        ):
            raise ValueError(
                f"Context sourcetype field mismatch: expected {expected_sourcetype.value}, "
                f"got {self.llm_context.sourcetype.value}"
            )

        # Check SyntheticData if present
        if self.synthetic_data:
            expected_synthetic_class = f"{expected_sourcetype.value}SyntheticData"
            actual_synthetic_class = self.synthetic_data.__class__.__name__
            if expected_synthetic_class != actual_synthetic_class:
                raise ValueError(
                    f"SyntheticData class mismatch for {expected_sourcetype.value}: "
                    f"expected {expected_synthetic_class}, got {actual_synthetic_class}"
                )

            if (
                hasattr(self.synthetic_data, "sourcetype")
                and self.synthetic_data.sourcetype != expected_sourcetype
            ):
                raise ValueError(
                    f"SyntheticData sourcetype field mismatch: expected {expected_sourcetype.value}, "
                    f"got {self.synthetic_data.sourcetype.value}"
                )

    def touch(self) -> None:
        """
        Update the updated_at timestamp
        """
        self.updated_at = int(time.time())

    @classmethod
    def create_with_embeddings(
        cls, content: "ProcessedContent"
    ) -> tuple["ProcessedContent", dict]:
        """
        Class method that generates embeddings for database insertion.

        Returns:
            tuple: (ProcessedContent object, embedding_data dict)
        """
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = {}

        if content.synthetic_data:
            try:
                if content.synthetic_data.description:
                    embeddings["description_embedding"] = model.encode(
                        content.synthetic_data.description
                    ).tolist()
            except:
                pass

            try:
                if content.synthetic_data.summary:
                    embeddings["summary_embedding"] = model.encode(
                        content.synthetic_data.summary
                    ).tolist()
            except:
                pass

        return content, embeddings

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
        uri = URI.from_source(
            data["source"], skip_checksum=True
        )  # skip checksum since paths are host-specific
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
        global count
        count += 1
        print(f"##      {count}")
        print(data["context_data"])
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

    @override
    def __str__(self) -> str:
        # Return a pretty printed json representation for easy logging -- truncate strings > 100 chars
        import json

        json_dict = self.model_dump()
        for key, value in json_dict.items():
            if isinstance(value, str) and len(value) > 100:
                json_dict[key] = value[:100] + "..."
        indented = json.dumps(json_dict, indent=2)
        return indented

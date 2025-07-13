"""
ProcessedContent is our final output format for content processed by Siphon.
It combines our URI, LLM context, and synthetic data into a structured format, for storage / caching / retrieval from postgres.
Our CLI also has a nice display method (.pretty_print()), which we add as a mixin to this class.
"""


from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.Context import Context
from Siphon.data.ProcessedContentDisplay import ProcessedContentDisplayMixin
from pydantic import BaseModel, Field
from typing import Optional


class ProcessedContent(BaseModel, ProcessedContentDisplayMixin):
    # Primary identifiers
    uri: URI = Field(
        ..., description="Original URI of the content, used for retrieval"
    )

    # AI context for LLM consumption
    llm_context: Context = Field(
        ..., description="Processed content + metadata ready for LLM consumption"
    )

    # Synthetic data (title, description, summary, topics, entities) -- added post init
    synthetic_data: Optional[SyntheticData] = Field(
        ..., description="AI-generated enrichments applied to the content"
    )

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

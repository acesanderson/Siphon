from Siphon.data.Metadata import SiphonMetadata
from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from pydantic import BaseModel, Field
from typing import Optional


class ProcessedContent(BaseModel):
    # Primary identifiers
    uri: URI = Field(
        ..., description="Original URI of the content, used for retrieval"
    )

    # Temporal data (as Unix timestamps)
    ## Record-specific time stamps
    ingested_at: int
    last_updated_at: int

    # Source-specific metadata (typed)
    metadata: SiphonMetadata = Field(
        default_factory=SiphonMetadata,
        description="Source-specific metadata, such as file size, author, etc.",
    )    # Core processed data

    # AI context for LLM consumption
    llm_context: str = Field(
        ..., description="Processed content ready for LLM consumption"
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
    def summary(self) -> str:
        """Summary of the content, derived from synthetic data if available."""
        return self.synthetic_data.summary if self.synthetic_data else ""




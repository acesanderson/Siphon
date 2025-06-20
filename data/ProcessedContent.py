from Siphon.data.Metadata import SiphonMetadata
from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from pydantic import BaseModel, Field
from typing import Optional


class ProcessedContent(BaseModel):
    # Primary identifiers
    content_id: str = Field(
        ..., description="Unique identifier for the content, a hash or doc ID"
    )
    uri: URI = Field(
        ..., description="Original URI of the content, used for retrieval"
    )

    # Temporal data (as Unix timestamps)
    ## Record-specific time stamps
    ingested_at: int
    last_updated_at: int

    # Core processed data
    llm_context: str = Field(
        ..., description="Processed content ready for LLM consumption"
    )

    # Synthetic data (title, description, summary, topics, entities) -- added post init
    synthetic_data: Optional[SyntheticData] = Field(
        default=None, description="AI-generated enrichments applied to the content"
    )

    # Source-specific metadata (typed)
    metadata: SiphonMetadata = Field(
        default_factory=SiphonMetadata,
        description="Source-specific metadata, such as file size, author, etc.",
    )

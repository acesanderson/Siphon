from Siphon.data.URI import URI
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class CLIParams(BaseModel):
    source: str = Field(
        ..., description="Path to the file or URL to retrieve context from"
    )
    return_type: Optional[Literal["m", "c", "s"]] = Field(
        default="s",
        description="Type of data to return: 'metadata', 'context', or 'synthetic_data'. Defaults to 'synthetic_data', i.e. a summary.",
    )

    # flags
    persist: bool = Field(
        default=False,
        description="Persist the processed content to disk. Eventually this will be True by default.",
    )
    llm: bool = Field(
        default=False, description="Use cloud LLM for conversion if applicable."
    )

    @field_validator("source")
    def validate_source(cls, v):
        uri = URI.from_source(v)
        if not uri:
            raise ValueError(f"Invalid source: {v}. Must be a valid file path or URL.")
        return v

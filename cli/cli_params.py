from Siphon.data.URI import URI
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class CLIParams(BaseModel):
    source: str = Field(
        ..., description="Path to the file or URL to retrieve context from"
    )
    cache_options: Optional[Literal["c", "u", "r"]] = Field(
        default="c",
        description="Special cache flags: 'u' (uncached, do not save), or 'r' (recache, save again). 'c' is default (cache the content).",
    )

    cloud: bool = Field(
        default=False, description="Use cloud LLMs for synthetic data if applicable."
    )

    tags: list[str] = Field(
        default_factory=list, description="Tags to apply to the context."
    )

    @field_validator("source")
    def validate_source(cls, v):
        uri = URI.from_source(v)
        if not uri:
            raise ValueError(f"Invalid source: {v}. Must be a valid file path or URL.")
        return v

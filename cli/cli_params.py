"""
CLI parameters for the Siphon tool.

These parameters can be provided via command-line arguments or programmatically.

Note: there are two major sources of context: addressable content (source) and ephemeral content (content + content_type).
Addressable content is content that can be retrieved from a file path or URL. This is specified via the `source` parameter.
Ephemeral content is content that is provided directly, such as pasted text or images from the clipboard. This is specified via the `content` and `content_type` parameters.

Ephemeral: existence precedes essence.
Addressable: essence precedes existence.
"""

from Siphon.data.URI import URI
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class CLIParams(BaseModel):
    # Addressable content, like files or URLs
    source: Optional[str] = Field(
        ..., description="Path to the file or URL to retrieve context from"
    )
    # Ephemeral content, like pasted text or images from clipboard
    content: Optional[str] = Field(
        default=None, description="Direct content to use as context"
    )
    content_type: Optional[str] = Field(
        default=None,
        description="Ephemeral sources, like stdin, pasted text, images from clipboard. This informs URI.",
    )
    # Request parameters
    cache_options: Optional[Literal["c", "u", "r"]] = Field(
        default="c",
        description="Special cache flags: 'u' (uncached, do not save), or 'r' (recache, save again). 'c' is default (cache the content).",
    )
    cloud: bool = Field(
        default=False, description="Use cloud LLMs for synthetic data if applicable."
    )
    # User metadata
    tags: list[str] = Field(
        default_factory=list, description="Tags to apply to the context."
    )

    @field_validator("source")
    def validate_source(cls, v):
        """
        If we have a source, validate that it is a valid file path or URL.
        """
        if v is None:
            return v
        uri = URI.from_source(v)
        if not uri:
            raise ValueError(f"Invalid source: {v}. Must be a valid file path or URL.")
        return v

    @field_validator("content", "content_type", mode="after")
    def validate_content_and_source(cls, v, info):
        """
        Ensure that either source is provided, or both content and content_type are provided.
        """
        source = info.data.get("source")
        content = info.data.get("content")
        content_type = info.data.get("content_type")

        if source and (content or content_type):
            raise ValueError("Cannot provide both source and content/content_type.")
        if not source and (not content or not content_type):
            raise ValueError(
                "Must provide either source or both content and content_type."
            )
        return v

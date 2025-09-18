from Siphon.data.Context import Context
from Siphon.data.types.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override, Literal, Optional
from pydantic import Field
import time


class EphemeralContext(Context):
    """
    Context class for handling text files.
    This is also the base class for audio, image, video, and obsidian contexts.
    """

    sourcetype: SourceType = SourceType.EPHEMERAL

    # Metadata field
    content_type: str
    capture_timestamp: int = Field(default_factory=lambda: int(time.time()))
    content_encoding: str = "utf-8"
    mime_type: Optional[str] = None

    @override
    @classmethod
    def from_uri(cls, uri: URI, model: Literal["local", "cloud"] = "cloud") -> Context:  # type: ignore
        """
        Create a Context from a URI.
        """
        raise NotImplementedError("EphemeralContext does not support from_uri method.")

    @classmethod
    def from_content(cls, content: str, content_type: str) -> Context:
        """
        Create a Context from raw content.
        """
        if not content:
            raise ValueError("Content cannot be empty.")
        if not isinstance(content, str):
            raise TypeError("Content must be a string.")
        if not content_type:
            raise ValueError("Content type cannot be empty.")
        if not isinstance(content_type, str):
            raise TypeError("Content type must be a string.")

        # Assemble and return the Context instance
        return cls(context=content, content_type=content_type, mime_type="text/plain")

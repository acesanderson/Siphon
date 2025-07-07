"""
High level wrapper for retrieving LLM context from various sources.
"""

from Siphon.ingestion.file_context import retrieve_file_context
from Siphon.ingestion.online_context import retrieve_online_context
from Siphon.data.URI import URI
from pathlib import Path


def retrieve_llm_context(uri: URI) -> str:
    """
    Generate llm_context from a file or online resource.
    Accepts a URI object, returns a rich string representation of the context.
    """
    if uri.source_type in ["ARTICLE", "YOUTUBE", "DRIVE", "GITHUB"]:
        return retrieve_online_context(uri.source)
    elif uri.source_type in ["OBSIDIAN", "FILE"]:
        file_path = Path(uri.source)
        return retrieve_file_context(file_path)
    elif uri.source_type == "email":
        raise NotImplementedError("Email source type is not yet implemented.")
    else:
        raise ValueError(
            f"Unsupported source type: {uri.source_type}. Supported types are: article, youtube, drive, github, obsidian, file."
        )

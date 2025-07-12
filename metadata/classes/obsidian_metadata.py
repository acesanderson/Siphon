"""
All file sourcetypes have the same metadata fields.
This has that + more.
"""

from Siphon.metadata.classes.text_metadata import TextMetadata
from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from typing import Literal, Optional, override


class ObsidianMetadata(TextMetadata):
    """Inherits and mixes with FileMetadata for Obsidian-specific notes."""

    sourcetype: SourceType = SourceType.OBSIDIAN

    note_path: str
    wiki_links: Optional[list[str]] = None
    urls: Optional[list[str]] = None
    note_type: Literal["daily", "code_project", "organization", "topic", "generic"] = (
        "generic"
    )

    @override
    @classmethod
    def from_URI(cls, uri: URI):
        """
        Parse Obsidian-specific content from the file.
        This is a placeholder for actual parsing logic.
        """
        # For now, we will just return an empty dict
        # In a real implementation, this would extract wiki links, note type, etc.
        # return {
        #     "note_path": file_path,
        #     "wiki_links": [],
        #     "note_type": None
        # }
        raise NotImplementedError("Obsidian content parsing not implemented yet.")

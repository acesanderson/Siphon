from Siphon.metadata.file_metadata import FileMetadata
from Siphon.data.URI import URI
from typing import Literal


class ObsidianMetadata(FileMetadata):
    """Inherits and mixes with FileMetadata for Obsidian-specific notes."""

    note_path: str
    wiki_links: list[str] = []
    urls: list[str] = []
    note_type: Literal["daily", "code_project", "organization", "topic", "generic"] = (
        "generic"
    )

    @classmethod
    def _parse_obsidian_content(cls, file_path: str):
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

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create ObsidianMetadata from a URI object.
        This method first retrieves the file metadata and then parses Obsidian-specific content.
        """
        # Get file metadata first
        file_data = FileMetadata.from_uri(uri)

        # Add Obsidian-specific parsing
        obsidian_data = cls._parse_obsidian_content(uri.source)

        # Combine and create instance
        return cls(**file_data, **obsidian_data)

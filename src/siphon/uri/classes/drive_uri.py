from siphon.data.uri import URI
from siphon.data.type_definitions.source_type import SourceType
from pydantic import Field
import re
from typing import override


class DriveURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.DRIVE,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        ...
        # def is_drive_url(url: str) -> bool:
        #     # Fix 2: Include docs.google.com in detection
        #     return (
        #         "docs.google.com" in url
        #         or "drive.google.com" in url
        #         or "drive.googleusercontent.com" in url
        #     )

    @override
    @classmethod
    def from_source(cls, source: str, skip_checksum: bool = False) -> "DriveURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        _ = skip_checksum  # currently unused
        ...

    @classmethod
    def _parse_drive_url(cls, url: str) -> tuple[str, SourceType, str]:
        """
        Parse Google Drive/Docs URLs - Fix 5: Extract file ID properly
        """

        # Google URLs format: https://docs.google.com/document/d/FILE_ID/edit
        # Or: https://drive.google.com/file/d/FILE_ID/view

        # Extract file ID using regex
        file_id_pattern = r"/d/([a-zA-Z0-9-_]+)"
        file_id_match = re.search(file_id_pattern, url)

        if not file_id_match:
            raise ValueError(f"Cannot extract file ID from Google URL: {url}")

        file_id = file_id_match.group(1)

        # Determine file type from URL path
        if "/spreadsheets/" in url:
            file_type = "sheet"
        elif "/presentation/" in url:
            file_type = "slide"
        elif "/document/" in url:
            file_type = "doc"
        elif "/forms/" in url:
            file_type = "form"
        else:
            # Default to doc if we can't determine
            file_type = "doc"

        uri = f"drive://{file_type}/{file_id}"
        return url, SourceType.DRIVE, uri

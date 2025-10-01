from siphon.data.uri import URI
from siphon.data.types.source_type import SourceType
from siphon.data.types.uri_schemes import URISchemes
from siphon.logs.logging_config import get_logger
from urllib.parse import urlparse
from pydantic import Field
from typing import override

logger = get_logger(__name__)


class GitHubURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    sourcetype: SourceType = Field(
        default=SourceType.GITHUB,
        description="The type of source this URI represents.",
    )

    @override
    @classmethod
    def identify(cls, source: str) -> bool:
        """
        Check if the source string matches the GitHub URI format.
        """
        return "github.com" in source

    @override
    @classmethod
    def from_source(
        cls, source: str, skip_checksum: bool = False
    ) -> "GitHubURI | None":  # type: ignore
        """
        Create an GitHubURI object from a source string.
        """
        _ = skip_checksum  # Unused for GitHub URIs
        parsed = urlparse(source)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format - missing owner/repo")

        owner = path_parts[0]
        repo = path_parts[1]

        # Handle different GitHub URL formats:
        # https://github.com/owner/repo
        # https://github.com/owner/repo/blob/branch/file.py
        # https://github.com/owner/repo/tree/branch/path

        if len(path_parts) > 3 and path_parts[2] in ["blob", "tree"]:
            # Format: /owner/repo/blob/branch/path/to/file
            file_path = "/".join(path_parts[4:]) if len(path_parts) > 4 else ""
        elif len(path_parts) > 2:
            # Format: /owner/repo/path/to/file (direct path)
            file_path = "/".join(path_parts[2:])
        else:
            # Format: /owner/repo (no file path)
            file_path = ""

        # Fix 3: Don't add trailing slash when no file path
        uri = f"{URISchemes['GitHub']}://{owner}/{repo}"
        if file_path:
            uri += f"/{file_path}"

        # Add fragment if present (for line numbers, etc.)
        if parsed.fragment:
            uri += f"#{parsed.fragment}"

        return cls(
            source=source,
            uri=uri,
        )

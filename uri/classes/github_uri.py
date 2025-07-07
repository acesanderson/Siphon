from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from pydantic import Field


class GitHubURI(URI):
    """
    Represents an article URI with metadata.
    Inherits from Metadata to include additional metadata fields.
    """

    source_type: SourceType = Field(
        default=SourceType.GITHUB,
        description="The type of source this URI represents.",
    )

    @classmethod
    def identify(cls, source: str) -> bool: ...

    @classmethod
    def from_source(cls, source: str) -> "GitHubURI | None":
        """
        Create an ArticleURI object from a source string.
        """
        ...

    @classmethod
    def _parse_github_url(cls, url: str) -> tuple[str, SourceType, str]:
        """
        Parse GitHub URLs.
        """
        parsed = urlparse(url)
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
        uri = f"github://{owner}/{repo}"
        if file_path:
            uri += f"/{file_path}"

        # Add fragment if present (for line numbers, etc.)
        if parsed.fragment:
            uri += f"#{parsed.fragment}"

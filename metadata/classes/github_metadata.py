from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI
from Siphon.data.SourceType import SourceType
from typing import override


class GitHubMetadata(Metadata):
    sourcetype: SourceType = SourceType.GITHUB
    repository_name: str
    file_path_in_repo: str
    branch_name: str = "main"

    @override
    @classmethod
    def from_uri(cls, uri: URI):
        """
        Factory method to create GitHubMetadata from a URI object.
        Extracts repository name, file path, and branch name from the URI.
        """
        from urllib.parse import urlparse

        parsed_url = urlparse(uri.source)
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid GitHub URL format")

        raise NotImplementedError("GitHubMetadata parsing not implemented yet.")

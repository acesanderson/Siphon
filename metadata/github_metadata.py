from Siphon.data.Metadata import Metadata
from Siphon.data.URI import URI


class GitHubMetadata(Metadata):
    repository_name: str
    file_path_in_repo: str
    branch_name: str = "main"

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

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory method to create ArticleMetadata from a dictionary.
        """
        ...

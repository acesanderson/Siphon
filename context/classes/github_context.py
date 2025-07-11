from Siphon.data.Context import Context
from Siphon.data.SourceType import SourceType
from Siphon.data.URI import URI
from typing import override


class GitHubContext(Context):
    sourcetype: SourceType = SourceType.GITHUB

    @override
    @classmethod
    def from_uri(cls, uri: "GitHubURI") -> "GitHubContext":  # type: ignore
        """
        Create a GitHubContext from a URI.
        """
        from Siphon.uri.classes.github_uri import GitHubURI

        if not isinstance(uri, GitHubURI):
            raise TypeError("Expected uri to be an instance of GitHubURI.")

        raise NotImplementedError("GitHubContext.from_uri is not implemented yet")

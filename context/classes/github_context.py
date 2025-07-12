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

        from Siphon.ingestion.github.retrieve_github import retrieve_github
        llm_context = retrieve_github(uri.source)
        assert isinstance(llm_context, str) and len(llm_context) > 0, "Expected llm_context to be a non-empty string."
        return cls(
            context=llm_context,
        )


from siphon.ingestion.github.flatten_url import flatten_github_repo


def retrieve_github(url: str) -> tuple[str, dict]:
    """
    Retrieve and flatten a GitHub repository URL.

    Args:
        url: GitHub repository URL
    Returns:
        A tuple containing:
            Flattened XML string of the repository
            Metadata dictionary with repository details
    """
    llm_context, metadata = flatten_github_repo(url)
    return llm_context, metadata

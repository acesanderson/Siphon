from Siphon.ingestion.github.flatten_url import flatten_github_repo


def retrieve_github(url: str) -> str:
    """
    Retrieve and flatten a GitHub repository URL.

    Args:
        url: GitHub repository URL
    Returns:
        Flattened XML string of the repository
    """
    return flatten_github_repo(url)

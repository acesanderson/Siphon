"""
This is adapted from leviathan main script. Within Siphon, this routes a url (passed with -u to Siphon) to either YouTube or an online article.
"""

from siphon.ingestion.youtube.retrieve_youtube import retrieve_youtube
from siphon.ingestion.github.retrieve_github import retrieve_github
from siphon.ingestion.googledrive.retrieve_google_doc import retrieve_google_doc
from siphon.ingestion.article.retrieve_article import retrieve_article


def categorize_url(url: str) -> str:
    """
    Determine the type of URL.
    """
    if "youtube" in url:
        return "youtube"
    if "github" in url:
        return "github"
    if "docs.google.com" in url:
        return "drive"
    if "arxib" in url:
        return "arxiv"
    elif "http" in url:
        return "article"
    else:
        raise ValueError("Input must be a YouTube URL or an article URL.")


def retrieve_online_context(url: str) -> str:
    """
    This function takes a URL and returns the text.
    """
    mode = categorize_url(url)
    match mode:
        case "youtube":
            return retrieve_youtube(url)
        case "github":
            return retrieve_github(url)
        case "drive":
            return retrieve_google_doc(url)
        case "article":
            return retrieve_article(url)
        case "arxiv":
            raise NotImplementedError("Arxiv not implemented yet.")
        case _:
            raise ValueError(f"Unsupported URL type: {mode}")

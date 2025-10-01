from siphon.ingestion.article.download_article import download_article
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from newspaper import Article


def retrieve_article(url: str) -> "Article":
    """
    Retrieve the article from a given URL.
    Note: this is an Article object; Article.text will give you the text of the article.
    """
    article = download_article(url)
    return article

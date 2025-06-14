"""
This is adapted from leviathan main script. Within Siphon, this routes a url (passed with -u to Siphon) to either YouTube or an online article.
"""

from Siphon.ingestion.articles.download_article import download_article
from Siphon.ingestion.youtube.download_youtube_transcript import (
    download_youtube_transcript,
)
from Chain import Prompt, Chain, Model
from utils.print_markdown import print_markdown
from typing import Literal
import argparse, sys
from pathlib import Path

dir_path = Path(__file__).parent
prompts_dir = dir_path.parent / "prompts"
format_prompt_file = prompts_dir / "format_transcript.jinja2"


def categorize_url(url: str) -> Literal["youtube", "article"]:
    """
    Determine the type of URL.
    """
    if "youtube" in url:
        return "youtube"
    elif "http" in url:
        return "article"
    else:
        raise ValueError("Input must be a YouTube URL or an article URL.")


def format_transcript(transcript: str, preferred_model: str = "claude") -> str:
    """
    This function takes a raw transcript and formats it.
    """
    model = Model(preferred_model)
    prompt = Prompt(format_prompt_file.read_text())
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"transcript": transcript}, verbose=True)
    return str(response.content)


def retrieve_online_context(url: str) -> str:
    """
    This function takes a URL and returns the text.
    """
    mode = categorize_url(url)
    match mode:
        case "youtube":
            transcript = download_youtube_transcript(url)
            formatted = format_transcript(transcript)
            return formatted
        case "article":
            return download_article(url)


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=tk3xzg_-Qh4"
    output = retrieve_online_context(youtube_url)
    print(output)

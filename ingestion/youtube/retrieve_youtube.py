from Siphon.ingestion.youtube.download_youtube_transcript import (
    download_youtube_transcript,
)
from Siphon.ingestion.youtube.format_youtube import format_youtube


def retrieve_youtube(url: str) -> str:
    transcript = download_youtube_transcript(url)
    if not transcript:
        raise ValueError(f"No transcript found for URL: {url}")
    formatted_transcript = format_youtube(transcript)
    return formatted_transcript

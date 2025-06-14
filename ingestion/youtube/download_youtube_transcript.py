"""
From module creator:

    *This code uses an undocumented part of the YouTube API, which is called by the YouTube web-client.
    So there is no guarantee that it won't stop working tomorrow, if they change how things work. I will
    however do my best to make things working again as soon as possible if that happens. So if it stops
    working, let me know!*

"""

from youtube_transcript_api import YouTubeTranscriptApi
import sys
import re

video_id = "5xb6uWLtCsI"
example = "https://www.youtube.com/watch?v=VctsqOo8wsc&t=628s"


def validate_video_id(input):
    """
    Validates that user has entered a valid YouTube Video ID, or a valid YouTube URL.
    """
    if re.match(r"^[a-zA-Z0-9_-]{11}$", input):
        return input
    elif re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})", input
    ):
        return re.match(
            r"^https?:\/\/(www\.)?youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})", input
        ).group(2)
    # also match for urls that have "live" instead of the standard "watch" https://www.youtube.com/live/OOdtmCMSOo4
    elif re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})", input
    ):
        return re.match(
            r"^https?:\/\/(www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})", input
        ).group(2)
    else:
        return ValueError("Invalid YouTube URL or Video ID")


def download_youtube_transcript(video_id) -> str:
    """
    Feed this either a youtube link or a youtube video id, and it will return the transcript of the video.
    """
    video_id = validate_video_id(video_id)
    t = YouTubeTranscriptApi.get_transcript(video_id)
    script = " ".join([line["text"] for line in t])
    return script


if __name__ == "__main__":
    video_id = "5xb6uWLtCsI"
    # video_id = "dQw4w9WgXcQ"
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    print(download_youtube_transcript(video_id))

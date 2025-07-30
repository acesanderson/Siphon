"""
YouTube CLI tool for handling playlists and channels.
Extends Siphon functionality without modifying core YouTubeURI class.

Usage:
   # Regular video (existing functionality)
   python scripts/youtube_cli.py "https://youtube.com/watch?v=abc123"

   # Playlist (siphon all videos, return combined transcript)
   python scripts/youtube_cli.py "https://youtube.com/playlist?list=PLxxx"

   # Channel (return video URL list)
   python scripts/youtube_cli.py "https://youtube.com/@channelname"
"""

import argparse
import os
import re
import sys
import time
from googleapiclient.discovery import build
from Siphon.main.siphon import siphon


def get_youtube_service():
    """Initialize YouTube Data API client."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)

    # NOTE: May need to handle API client initialization errors
    return build("youtube", "v3", developerKey=api_key)


def extract_playlist_id(url):
    """Extract playlist ID from YouTube playlist URL."""
    # NOTE: This regex might not catch all playlist URL variations
    match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None


def extract_channel_info(url):
    """Extract channel identifier from various YouTube channel URL formats."""
    # NOTE: YouTube channel URL formats may change - these patterns might need updates

    # @username format
    if "@" in url:
        match = re.search(r"@([a-zA-Z0-9_-]+)", url)
        return ("username", match.group(1)) if match else (None, None)

    # /channel/UC... format
    if "/channel/" in url:
        match = re.search(r"/channel/([a-zA-Z0-9_-]+)", url)
        return ("channel_id", match.group(1)) if match else (None, None)

    # /c/customname or /user/username formats
    if "/c/" in url or "/user/" in url:
        match = re.search(r"/(?:c|user)/([a-zA-Z0-9_-]+)", url)
        return ("username", match.group(1)) if match else (None, None)

    return (None, None)


def get_channel_uploads_playlist(service, channel_type, channel_value):
    """Get the uploads playlist ID for a channel."""
    try:
        if channel_type == "channel_id":
            request = service.channels().list(part="contentDetails", id=channel_value)
        else:  # username
            # NOTE: forUsername parameter might be deprecated - may need to use different approach
            request = service.channels().list(
                part="contentDetails", forUsername=channel_value
            )

        response = request.execute()

        if not response["items"]:
            print(f"Error: Channel not found")
            return None

        # NOTE: uploads playlist ID pattern (UC -> UU) might change
        uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        return uploads_playlist

    except Exception as e:
        print(f"Error fetching channel info: {e}")
        return None


def get_playlist_videos(service, playlist_id, max_results=50):
    """Get video IDs from a playlist."""
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        try:
            request = service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(
                    50, max_results - len(videos)
                ),  # API max is 50 per request
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                # NOTE: Video might be private/deleted - snippet might not have videoId
                video_id = item["snippet"]["resourceId"].get("videoId")
                title = item["snippet"]["title"]
                if video_id:
                    videos.append({"id": video_id, "title": title})

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"Error fetching playlist videos: {e}")
            break

    return videos[:max_results]


def handle_playlist(url):
    """Process YouTube playlist - siphon all videos and return combined transcript."""
    playlist_id = extract_playlist_id(url)
    if not playlist_id:
        print("Error: Could not extract playlist ID from URL")
        return

    service = get_youtube_service()
    videos = get_playlist_videos(service, playlist_id, max_results=20)

    if not videos:
        print("Error: No videos found in playlist")
        return

    print(f"Processing {len(videos)} videos from playlist...")
    combined_transcript = []

    for video in videos:
        video_url = f"https://youtube.com/watch?v={video['id']}"
        print(f"Processing: {video['title']}")

        try:
            processed_content = siphon(video_url)
            separator = f"=== {video['title']} ({video_url}) ==="
            combined_transcript.append(separator)
            combined_transcript.append(processed_content.context)
            combined_transcript.append("")  # Empty line between videos

        except Exception as e:
            print(f"Error processing {video_url} - {video['title']}: {e}")
            continue

        time.sleep(1)  # Rate limiting

    # Print combined result
    print("\n" + "=" * 80)
    print("COMBINED PLAYLIST TRANSCRIPT")
    print("=" * 80 + "\n")
    print("\n".join(combined_transcript))


def handle_channel(url):
    """Process YouTube channel - return list of video URLs."""
    channel_type, channel_value = extract_channel_info(url)
    if not channel_type:
        print("Error: Could not extract channel info from URL")
        return

    service = get_youtube_service()
    uploads_playlist = get_channel_uploads_playlist(
        service, channel_type, channel_value
    )

    if not uploads_playlist:
        return

    videos = get_playlist_videos(service, uploads_playlist, max_results=50)

    print(f"Found {len(videos)} videos in channel:")
    for video in videos:
        print(f"https://youtube.com/watch?v={video['id']}")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube playlist and channel processor"
    )
    parser.add_argument("url", help="YouTube video, playlist, or channel URL")
    args = parser.parse_args()

    url = args.url.strip()

    if "playlist?list=" in url:
        handle_playlist(url)
    elif any(x in url for x in ["@", "/channel/", "/c/", "/user/"]):
        handle_channel(url)
    else:
        # Regular video - just siphon it
        try:
            processed_content = siphon(url)
            processed_content.pretty_print()
        except Exception as e:
            print(f"Error processing video: {e}")


if __name__ == "__main__":
    main()

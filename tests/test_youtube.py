#!/usr/bin/env python3
"""
Test script for YouTube channel URL extraction.
"""

import os
import sys
from googleapiclient.discovery import build


def test_channel_urls():
    """Test extracting URLs from @aiDotEngineer channel."""

    # Check for API key
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize YouTube service
    service = build("youtube", "v3", developerKey=api_key)

    # Get channel info for @aiDotEngineer
    try:
        # First get channel ID from username
        search_response = (
            service.search()
            .list(part="snippet", q="aiDotEngineer", type="channel", maxResults=1)
            .execute()
        )

        if not search_response["items"]:
            print("Channel not found")
            return

        channel_id = search_response["items"][0]["snippet"]["channelId"]
        print(f"Found channel ID: {channel_id}")

        # Get channel details to find uploads playlist
        channel_response = (
            service.channels().list(part="contentDetails", id=channel_id).execute()
        )

        uploads_playlist = channel_response["items"][0]["contentDetails"][
            "relatedPlaylists"
        ]["uploads"]
        print(f"Uploads playlist: {uploads_playlist}")

        # Get videos from uploads playlist
        videos_response = (
            service.playlistItems()
            .list(part="snippet", playlistId=uploads_playlist, maxResults=50)
            .execute()
        )

        print(f"\nFound {len(videos_response['items'])} videos:")
        for item in videos_response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            title = item["snippet"]["title"]
            url = f"https://youtube.com/watch?v={video_id}"
            print(f"{url}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_channel_urls()

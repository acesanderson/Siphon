"""
ContentID inherits from String, with constructor methods.
"""

from Siphon.data.URI import URI
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional
import hashlib, re

class ContentID(str):
    """
    ContentID is a class that represents a content identifier.
    It is used to uniquely identify content in the system.
    """

    def __new__(cls, value: str):
        """
        Initialize the ContentID with a string value.
        :param value: The content identifier as a string.
        """
        return super().__new__(cls, value)

    @classmethod
    def from_uri(cls, uri: URI):
        """
        Create a ContentID from a URI.
        :param uri: The URI to create the ContentID from.
        :return: A ContentID instance.
        """
        match uri.source_type:
            case "youtube":
                youtube_url = uri.source
                youtube_id = cls.generate_youtube_content_id(youtube_url)
                if youtube_id is None:
                    raise ValueError(f"Invalid YouTube URL: {youtube_url}")
                return cls(youtube_id)
            case "file":
                file_path = uri.source
                file_hash = cls.generate_file_hash(file_path)
                return cls(file_hash)
            case "article":
                article_url = uri.source
                return cls(cls.generate_online_content_id(article_url))
            case "github":
                github_url = uri.source
                github_hash = cls.generate_github_hash(github_url)
                return cls(github_hash)
            case "email":
                raise NotImplementedError("Email content ID generation is not implemented.")
            case "drive":
                drive_url = uri.source
                drive_id = cls.generate_drive_content_id(drive_url)
                return cls(drive_id)
            case "obsidian": # Same as file
                file_path = uri.source
                file_hash = cls.generate_file_hash(file_path)
                return cls(file_hash)
            case _:
                raise ValueError(f"Unsupported source type: {uri.source_type}")

    @classmethod
    def generate_youtube_content_id(cls, url: str) -> Optional[str]:
        """ Generate content ID for YouTube videos. """

        def extract_youtube_video_id(url: str) -> Optional[str]:
            """
            Extract YouTube video ID from various YouTube URL formats.
            
            Supports all common YouTube URL patterns:
            - https://www.youtube.com/watch?v=VIDEO_ID
            - https://youtu.be/VIDEO_ID
            - https://www.youtube.com/embed/VIDEO_ID
            - https://www.youtube.com/v/VIDEO_ID
            - https://m.youtube.com/watch?v=VIDEO_ID
            - https://music.youtube.com/watch?v=VIDEO_ID
            - YouTube URLs with additional parameters
            """
            if not url:
                return None
            
            # Clean the URL
            url = url.strip()
            
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Check if it's a YouTube domain
                youtube_domains = {
                    'youtube.com', 'www.youtube.com', 'm.youtube.com',
                    'music.youtube.com', 'youtu.be', 'www.youtu.be'
                }
                
                if not any(domain.endswith(yt_domain) for yt_domain in youtube_domains):
                    return None
                
                # Pattern 1: youtu.be/VIDEO_ID
                if 'youtu.be' in domain:
                    video_id = parsed.path.lstrip('/')
                    # Remove any additional path segments
                    video_id = video_id.split('/')[0]
                    if is_valid_youtube_id(video_id):
                        return video_id
                
                # Pattern 2: youtube.com/watch?v=VIDEO_ID
                elif parsed.path == '/watch':
                    query_params = parse_qs(parsed.query)
                    if 'v' in query_params:
                        video_id = query_params['v'][0]
                        if is_valid_youtube_id(video_id):
                            return video_id
                
                # Pattern 3: youtube.com/embed/VIDEO_ID
                elif parsed.path.startswith('/embed/'):
                    video_id = parsed.path.split('/embed/')[1]
                    # Remove any additional path segments
                    video_id = video_id.split('/')[0]
                    if is_valid_youtube_id(video_id):
                        return video_id
                
                # Pattern 4: youtube.com/v/VIDEO_ID
                elif parsed.path.startswith('/v/'):
                    video_id = parsed.path.split('/v/')[1]
                    # Remove any additional path segments
                    video_id = video_id.split('/')[0]
                    if is_valid_youtube_id(video_id):
                        return video_id
                
                # Pattern 5: youtube.com/watch/VIDEO_ID (less common)
                elif parsed.path.startswith('/watch/'):
                    video_id = parsed.path.split('/watch/')[1]
                    video_id = video_id.split('/')[0]
                    if is_valid_youtube_id(video_id):
                        return video_id
                
                # Fallback: Try to find video ID with regex in the entire URL
                # This catches edge cases and malformed URLs
                video_id_pattern = r'(?:v=|v\/|vi=|vi\/|youtu\.be\/|embed\/|watch\?.*v=)([a-zA-Z0-9_-]{11})'
                match = re.search(video_id_pattern, url)
                if match:
                    video_id = match.group(1)
                    if is_valid_youtube_id(video_id):
                        return video_id
            
            except Exception:
                # If URL parsing fails, try regex fallback
                video_id_pattern = r'(?:v=|v\/|vi=|vi\/|youtu\.be\/|embed\/|watch\?.*v=)([a-zA-Z0-9_-]{11})'
                match = re.search(video_id_pattern, url)
                if match:
                    video_id = match.group(1)
                    if is_valid_youtube_id(video_id):
                        return video_id
            
            return None

        def is_valid_youtube_id(video_id: str) -> bool:
            """
            Validate that a string is a valid YouTube video ID.
            
            YouTube video IDs are exactly 11 characters long and contain
            only letters, numbers, hyphens, and underscores.
            
            Args:
                video_id: String to validate
                
            Returns:
                True if valid YouTube video ID format
            """
            if not video_id or len(video_id) != 11:
                return False
            
            # YouTube IDs contain only letters, numbers, hyphens, and underscores
            pattern = r'^[a-zA-Z0-9_-]{11}$'
            return bool(re.match(pattern, video_id))

        return extract_youtube_video_id(url)

    @classmethod
    def generate_file_hash(cls, file_path: str) -> str:
        """Generate a content ID based on the file's hash."""
        with open(file_path, "rb") as file:
            file_content = file.read()
            return hashlib.sha256(file_content).hexdigest()

    @classmethod
    def generate_online_content_id(cls, url: str) -> str:
        """Generate content ID for online resources."""

        def normalize_url(url: str) -> str:
            """Normalize URL for consistent content ID generation."""
            parsed = urlparse(url.lower())
            
            # Remove common tracking parameters
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'msclkid', '_ga', 'ref', 'source'
            }
            
            # Filter out tracking parameters
            query_params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in query_params.items() 
                if k not in tracking_params
            }
            
            # Rebuild normalized URL
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path.rstrip('/'),  # Remove trailing slash
                parsed.params,
                urlencode(sorted(filtered_params.items())), # Sort for consistency
                ''  # Remove fragment/anchor
            ))
            
            return normalized

        normalized_url = normalize_url(url)
        return hashlib.sha256(normalized_url.encode('utf-8')).hexdigest()

    @classmethod
    def generate_github_hash(cls, repo_url: str) -> str:
        """Generate a content ID for GitHub files."""
        # create a hash based on owner/repo
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
        owner, repo = match.groups()
        # Normalize the repo URL
        normalized_url = f"{owner.lower()}/{repo.lower()}"
        # Generate a SHA-256 hash of the normalized URL
        normalized_url = re.sub(r'\.git$', '', normalized_url)
        normalized_url = re.sub(r'/$', '', normalized_url)
        normalized_url = re.sub(r'\s+', '', normalized_url)
        normalized_url = re.sub(r'[^a-zA-Z0-9_/]', '', normalized_url)
        if not normalized_url:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
        return hashlib.sha256(normalized_url.encode('utf-8')).hexdigest()

    @classmethod
    def generate_drive_content_id(cls, drive_url: str) -> str:
        """ Get the doc ID from a Google Drive URL. No hashing is done here. """
        match = re.search(r'/d/([^/]+)', drive_url)
        if not match:
            raise ValueError(f"Invalid Google Drive URL: {drive_url}")
        doc_id = match.group(1)
        return doc_id

    @classmethod
    def generate_email_hash(cls, email: str) -> str:
        """ Generate a content ID for email addresses. """
        raise NotImplementedError("Email content ID generation is not implemented yet.")


from Siphon.data.SourceType import SourceType
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, Field
from pathlib import Path
import re


class URI(BaseModel):
    source: str = Field(..., description="The original source URL, filepath, etc.")
    source_type: SourceType = Field(..., description="The type of source this URI represents.")
    uri: str = Field(..., description="The URI string representation of the source.")

    @classmethod
    def from_source(cls, source: str) -> "URI":
        """Create a URI object from a source string."""
        # Fix 1: Strip whitespace from input
        source = source.strip()
        source_string, source_type, uri = cls.parse_source(source)
        return cls(source=source_string, source_type=source_type, uri=uri)

    @classmethod
    def parse_source(cls, source: str) -> tuple[str, SourceType, str]:
        """Parse a source string into its components."""
        # Strip whitespace
        source = source.strip()
        
        def is_path(source: str) -> bool:
            """Check if the source is a valid file path."""
            return Path(source).exists()

        def is_url(source: str) -> bool:
            """Check if the source is a valid URL."""
            return source.startswith(("http://", "https://", "ftp://"))

        # Check URL first (more specific than file path)
        if is_url(source):
            return cls.parse_url(source)
        elif is_path(source):
            return cls.parse_file_path(str(source))
        else:
            raise ValueError(f"Unsupported source format: {source}")

    @classmethod
    def parse_url(cls, url: str) -> tuple[str, SourceType, str]:
        """Parse a URL into its components."""
        def is_github_url(url: str) -> bool:
            return "github.com" in url

        def is_youtube_url(url: str) -> bool:
            return "youtube.com" in url or "youtu.be" in url

        def is_drive_url(url: str) -> bool:
            # Fix 2: Include docs.google.com in detection
            return ("docs.google.com" in url or 
                    "drive.google.com" in url or 
                    "drive.googleusercontent.com" in url)

        def is_article_url(url: str) -> bool:
            return url.startswith(("http://", "https://"))

        # Order matters: most specific first
        if is_github_url(url):
            return cls._parse_github_url(url)
        elif is_youtube_url(url):
            return cls._parse_youtube_url(url)
        elif is_drive_url(url):
            return cls._parse_drive_url(url)
        elif is_article_url(url):
            return cls._parse_article_url(url)
        else:
            raise ValueError(f"Unsupported URL format: {url}")

    @classmethod
    def _parse_github_url(cls, url: str) -> tuple[str, SourceType, str]:
        """Parse GitHub URLs"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format - missing owner/repo")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        # Handle different GitHub URL formats:
        # https://github.com/owner/repo
        # https://github.com/owner/repo/blob/branch/file.py
        # https://github.com/owner/repo/tree/branch/path
        
        if len(path_parts) > 3 and path_parts[2] in ["blob", "tree"]:
            # Format: /owner/repo/blob/branch/path/to/file
            file_path = "/".join(path_parts[4:]) if len(path_parts) > 4 else ""
        elif len(path_parts) > 2:
            # Format: /owner/repo/path/to/file (direct path)
            file_path = "/".join(path_parts[2:])
        else:
            # Format: /owner/repo (no file path)
            file_path = ""
        
        # Fix 3: Don't add trailing slash when no file path
        uri = f"github://{owner}/{repo}"
        if file_path:
            uri += f"/{file_path}"
        
        # Add fragment if present (for line numbers, etc.)
        if parsed.fragment:
            uri += f"#{parsed.fragment}"
        
        return url, SourceType.GITHUB, uri

    @classmethod
    def _parse_youtube_url(cls, url: str) -> tuple[str, SourceType, str]:
        """Parse YouTube URLs - Fix 4: Extract video ID properly"""
        
        # Handle different YouTube URL formats:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://youtube.com/watch?v=VIDEO_ID&t=123
        
        if "youtu.be/" in url:
            # Short format: https://youtu.be/VIDEO_ID
            video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        else:
            # Long format: extract from query parameter
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            if 'v' not in query_params:
                raise ValueError(f"Cannot find video ID in YouTube URL: {url}")
            
            video_id = query_params['v'][0]
        
        # Validate video ID format (11 characters, alphanumeric + - and _)
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            raise ValueError(f"Invalid YouTube video ID format: {video_id}")
        
        uri = f"youtube://{video_id}"
        return url, SourceType.YOUTUBE, uri

    @classmethod
    def _parse_drive_url(cls, url: str) -> tuple[str, SourceType, str]:
        """Parse Google Drive/Docs URLs - Fix 5: Extract file ID properly"""
        
        # Google URLs format: https://docs.google.com/document/d/FILE_ID/edit
        # Or: https://drive.google.com/file/d/FILE_ID/view
        
        # Extract file ID using regex
        file_id_pattern = r'/d/([a-zA-Z0-9-_]+)'
        file_id_match = re.search(file_id_pattern, url)
        
        if not file_id_match:
            raise ValueError(f"Cannot extract file ID from Google URL: {url}")
        
        file_id = file_id_match.group(1)
        
        # Determine file type from URL path
        if "/spreadsheets/" in url:
            file_type = "sheet"
        elif "/presentation/" in url:
            file_type = "slide" 
        elif "/document/" in url:
            file_type = "doc"
        elif "/forms/" in url:
            file_type = "form"
        else:
            # Default to doc if we can't determine
            file_type = "doc"
        
        uri = f"drive://{file_type}/{file_id}"
        return url, SourceType.DRIVE, uri

    @classmethod
    def _parse_article_url(cls, url: str) -> tuple[str, SourceType, str]:
        """Parse generic article URLs"""
        # For articles, the URI is just the original URL
        return url, SourceType.ARTICLE, url

    @classmethod
    def parse_file_path(cls, file_path: str) -> tuple[str, SourceType, str]:
        """Parse a file path into its components."""
        
        # TODO: Add Obsidian detection logic here
        # from Siphon.ingestion.obsidian.vault import vault
        # For now, treat all files as generic files
        
        source_type = SourceType.FILE
        absolute_path = Path(file_path).resolve()
        uri = f"file://{absolute_path}"
        return str(absolute_path), source_type, uri

    def __repr__(self) -> str:
        """Clean, informative representation showing type and processed URI"""
        return f"URI({self.source_type.value}: '{self.uri}')"
    
    def __str__(self) -> str:
        """String representation is just the processed URI"""
        return self.uri



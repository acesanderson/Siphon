"""
Comprehensive test suite for URI parsing logic.
Tests all supported source string formats and edge cases.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Assuming your imports - adjust paths as needed
from Siphon.data.URI import URI
from Siphon.data.types.SourceType import SourceType


class TestURIFromSource:
    """Test the main entry point from_source method"""

    def test_valid_source_returns_uri_object(self):
        """Valid sources should return URI objects"""
        with patch.object(URI, "is_path", return_value=True):
            uri = URI.from_source("/path/to/file.txt")
            assert uri is not None
            assert isinstance(uri, URI)

    def test_invalid_source_returns_none(self):
        """Invalid sources should return None"""
        with (
            patch.object(URI, "is_path", return_value=False),
            patch.object(URI, "is_url", return_value=False),
        ):
            uri = URI.from_source("invalid://unsupported")
            assert uri is None

    def test_whitespace_stripped(self):
        """Whitespace should be stripped from source strings"""
        with patch.object(URI, "is_path", return_value=True):
            uri = URI.from_source("  /path/to/file.txt  ")
            assert uri.source == "/path/to/file.txt"


class TestURLParsing:
    """Test URL parsing for different platforms"""

    def test_github_repo_url(self):
        """Test basic GitHub repository URL"""
        url = "https://github.com/owner/repo"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.GITHUB
        assert uri == "github://owner/repo"

    def test_github_file_blob_url(self):
        """Test GitHub file blob URL"""
        url = "https://github.com/owner/repo/blob/main/src/file.py"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.GITHUB
        assert uri == "github://owner/repo/src/file.py"

    def test_github_tree_url(self):
        """Test GitHub tree/directory URL"""
        url = "https://github.com/owner/repo/tree/main/src/utils"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.GITHUB
        assert uri == "github://owner/repo/src/utils"

    def test_github_url_with_fragment(self):
        """Test GitHub URL with line number fragment"""
        url = "https://github.com/owner/repo/blob/main/file.py#L42"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.GITHUB
        assert uri == "github://owner/repo/file.py#L42"

    def test_github_invalid_url(self):
        """Test invalid GitHub URL missing repo"""
        url = "https://github.com/owner"
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            URI.parse_url(url)

    def test_youtube_watch_url(self):
        """Test standard YouTube watch URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.YOUTUBE
        assert uri == "youtube://dQw4w9WgXcQ"

    def test_youtube_short_url(self):
        """Test YouTube short URL format"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.YOUTUBE
        assert uri == "youtube://dQw4w9WgXcQ"

    def test_youtube_url_with_timestamp(self):
        """Test YouTube URL with timestamp parameter"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.YOUTUBE
        assert uri == "youtube://dQw4w9WgXcQ"

    def test_youtube_invalid_video_id(self):
        """Test YouTube URL with invalid video ID"""
        url = "https://www.youtube.com/watch?v=invalid"
        with pytest.raises(ValueError, match="Invalid YouTube video ID format"):
            URI.parse_url(url)

    def test_youtube_missing_video_id(self):
        """Test YouTube URL missing video ID"""
        url = "https://www.youtube.com/watch"
        with pytest.raises(ValueError, match="Cannot find video ID"):
            URI.parse_url(url)

    def test_google_docs_url(self):
        """Test Google Docs URL"""
        url = "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.DRIVE
        assert uri == "drive://doc/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

    def test_google_sheets_url(self):
        """Test Google Sheets URL"""
        url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.DRIVE
        assert uri == "drive://sheet/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

    def test_google_slides_url(self):
        """Test Google Slides URL"""
        url = "https://docs.google.com/presentation/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.DRIVE
        assert uri == "drive://slide/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

    def test_google_drive_file_url(self):
        """Test Google Drive file URL"""
        url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.DRIVE
        assert uri == "drive://doc/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

    def test_google_drive_invalid_url(self):
        """Test Google Drive URL without file ID"""
        url = "https://docs.google.com/document/"
        with pytest.raises(ValueError, match="Cannot extract file ID"):
            URI.parse_url(url)

    def test_generic_article_url(self):
        """Test generic article URL"""
        url = "https://example.com/article/great-post"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.ARTICLE
        assert uri == url

    def test_http_article_url(self):
        """Test HTTP (non-HTTPS) article URL"""
        url = "http://example.com/post"
        source, source_type, uri = URI.parse_url(url)

        assert source == url
        assert source_type == SourceType.ARTICLE
        assert uri == url


class TestFilePathParsing:
    """Test file path parsing"""

    def test_absolute_file_path(self):
        """Test absolute file path parsing"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name

        try:
            source, source_type, uri = URI.parse_file_path(file_path)

            assert source == str(Path(file_path).resolve())
            assert source_type == SourceType.FILE
            assert uri == f"file://{Path(file_path).resolve()}"
        finally:
            Path(file_path).unlink(missing_ok=True)

    def test_relative_file_path(self):
        """Test relative file path parsing"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name

        try:
            # Use relative path
            rel_path = Path(file_path).name
            cwd = Path.cwd()

            # Move file to current directory for relative access
            new_path = cwd / rel_path
            Path(file_path).rename(new_path)

            source, source_type, uri = URI.parse_file_path(rel_path)

            assert source == str(new_path)
            assert source_type == SourceType.FILE
            assert uri == f"file://{new_path}"
        finally:
            new_path.unlink(missing_ok=True)


class TestSourceDetection:
    """Test source type detection logic"""

    def test_url_detection_precedence(self):
        """URLs should be detected before file paths"""
        # Mock a scenario where a URL might also exist as a file
        with (
            patch.object(URI, "is_path", return_value=True),
            patch.object(URI, "is_url", return_value=True),
        ):
            source = "https://example.com/file"
            source_str, source_type, uri = URI.parse_source(source)

            # Should be parsed as URL, not file
            assert source_type == SourceType.ARTICLE

    def test_file_path_fallback(self):
        """File paths should be checked if not a URL"""
        with (
            patch.object(URI, "is_path", return_value=True),
            patch.object(URI, "is_url", return_value=False),
        ):
            source = "/path/to/file.txt"
            source_str, source_type, uri = URI.parse_source(source)

            assert source_type == SourceType.FILE


class TestCaching:
    """Test that caching works for URL and path detection"""

    def test_is_url_caching(self):
        """Test that is_url results are cached"""
        test_url = "https://example.com"

        # First call
        result1 = URI.is_url(test_url)
        # Second call should use cache
        result2 = URI.is_url(test_url)

        assert result1 == result2 == True

        # Verify cache info exists (indicates caching is working)
        assert hasattr(URI.is_url, "cache_info")

    def test_is_path_caching(self):
        """Test that is_path results are cached"""
        test_path = "/nonexistent/path"

        # First call
        result1 = URI.is_path(test_path)
        # Second call should use cache
        result2 = URI.is_path(test_path)

        assert result1 == result2 == False

        # Verify cache info exists
        assert hasattr(URI.is_path, "cache_info")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_string(self):
        """Test empty string handling"""
        with (
            patch.object(URI, "is_path", return_value=False),
            patch.object(URI, "is_url", return_value=False),
        ):
            with pytest.raises(ValueError, match="Unsupported source format"):
                URI.parse_source("")

    def test_whitespace_only_string(self):
        """Test whitespace-only string"""
        with (
            patch.object(URI, "is_path", return_value=False),
            patch.object(URI, "is_url", return_value=False),
        ):
            with pytest.raises(ValueError, match="Unsupported source format"):
                URI.parse_source("   ")

    def test_malformed_urls(self):
        """Test various malformed URLs"""
        malformed_urls = [
            "http://",
            "https://",
            "not-a-url",
            "github.com/owner/repo",  # Missing protocol
        ]

        for url in malformed_urls:
            with patch.object(URI, "is_path", return_value=False):
                if not URI.is_url(url):
                    with pytest.raises(ValueError):
                        URI.parse_source(url)


class TestURIObject:
    """Test URI object methods and properties"""

    def test_uri_repr(self):
        """Test URI string representation"""
        uri = URI(
            source="https://example.com",
            source_type=SourceType.ARTICLE,
            uri="https://example.com",
        )

        expected = "URI(ARTICLE: 'https://example.com')"
        assert repr(uri) == expected

    def test_uri_str(self):
        """Test URI string conversion"""
        uri = URI(
            source="https://example.com",
            source_type=SourceType.ARTICLE,
            uri="https://example.com",
        )

        assert str(uri) == "https://example.com"


# Integration test
class TestFullIntegration:
    """End-to-end integration tests"""

    @pytest.mark.parametrize(
        "source,expected_type,expected_uri_prefix",
        [
            ("https://github.com/owner/repo", SourceType.GITHUB, "github://"),
            (
                "https://youtube.com/watch?v=dQw4w9WgXcQ",
                SourceType.YOUTUBE,
                "youtube://",
            ),
            (
                "https://docs.google.com/document/d/abc123/edit",
                SourceType.DRIVE,
                "drive://",
            ),
            ("https://example.com/article", SourceType.ARTICLE, "https://"),
        ],
    )
    def test_full_parsing_pipeline(self, source, expected_type, expected_uri_prefix):
        """Test the complete parsing pipeline for various source types"""
        uri_obj = URI.from_source(source)

        assert uri_obj is not None
        assert uri_obj.source_type == expected_type
        assert uri_obj.uri.startswith(expected_uri_prefix)
        assert uri_obj.source == source

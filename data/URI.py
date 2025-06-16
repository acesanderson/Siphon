from urllib.parse import urlparse
from typing import Optional
from pydantic import BaseModel, field_validator
from pathlib import Path
import subprocess
import platform


class SiphonURI(BaseModel):
    """
    Represents a Siphon URI with parsing, validation, and navigation capabilities.

    Supported URI schemes:
    - file:///absolute/path/to/file
    - https://domain.com/path
    - obsidian://vault-name/path/to/note
    - github://owner/repo/path/to/file#commit-hash
    - sheets://spreadsheet-id/sheet-name?range=A1:C10
    - recording://timestamp-or-id
    - email://message-id/thread-id
    - drive://file-id
    """

    raw_uri: str
    scheme: str
    location: str  # netloc/host part (vault, owner/repo, etc.)
    path: str
    fragment: Optional[str] = None
    query: Optional[str] = None

    @field_validator("scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        supported_schemes = {
            "file",
            "https",
            "http",
            "obsidian",
            "github",
            "sheets",
            "recording",
            "email",
            "drive",
            "slack",
        }
        if v not in supported_schemes:
            raise ValueError(f"Unsupported URI scheme: {v}")
        return v

    @classmethod
    def from_string(cls, uri: str) -> "SiphonURI":
        """Parse a URI string into a SiphonURI object"""
        parsed = urlparse(uri)
        return cls(
            raw_uri=uri,
            scheme=parsed.scheme,
            location=parsed.netloc,
            path=parsed.path,
            fragment=parsed.fragment or None,
            query=parsed.query or None,
        )

    @classmethod
    def create_file_uri(cls, file_path: str | Path) -> "SiphonURI":
        """Create a file:// URI from a file path"""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        absolute_path = file_path.resolve()
        uri = f"file://{absolute_path}"
        return cls.from_string(uri)

    @classmethod
    def create_obsidian_uri(cls, vault: str, note_path: str) -> "SiphonURI":
        """Create an obsidian:// URI"""
        # Clean the note path
        clean_path = note_path.lstrip("/")
        uri = f"obsidian://{vault}/{clean_path}"
        return cls.from_string(uri)

    @classmethod
    def create_github_uri(
        cls, owner: str, repo: str, file_path: str = ""
    ) -> "SiphonURI":
        """Create a github:// URI"""
        clean_path = file_path.lstrip("/") if file_path else ""

        # Create URI with owner/repo as a single component
        if clean_path:
            uri = f"github://{owner}/{repo}/{clean_path}"
        else:
            uri = f"github://{owner}/{repo}"

        return cls.from_string(uri)

    @classmethod
    def create_sheets_uri(
        cls,
        spreadsheet_id: str,
        sheet_name: str = "Sheet1",
        range_spec: Optional[str] = None,
    ) -> "SiphonURI":
        """Create a sheets:// URI for Google Sheets"""
        uri = f"sheets://{spreadsheet_id}/{sheet_name}"
        if range_spec:
            uri += f"?range={range_spec}"
        return cls.from_string(uri)

    @classmethod
    def create_recording_uri(cls, recording_id: str) -> "SiphonURI":
        """Create a recording:// URI"""
        uri = f"recording://{recording_id}"
        return cls.from_string(uri)

    @classmethod
    def create_email_uri(
        cls, message_id: str, thread_id: Optional[str] = None
    ) -> "SiphonURI":
        """Create an email:// URI"""
        uri = f"email://{message_id}"
        if thread_id:
            uri += f"/{thread_id}"
        return cls.from_string(uri)

    @classmethod
    def create_drive_uri(cls, file_id: str) -> "SiphonURI":
        """Create a drive:// URI for Google Drive"""
        uri = f"drive://{file_id}"
        return cls.from_string(uri)

    def parse_github_components(self) -> tuple[str, str, str]:
        """Extract owner, repo, and file_path from GitHub URI"""
        if self.scheme != "github":
            raise ValueError("Not a GitHub URI")

        # For github://owner/repo/path/to/file
        # urlparse gives us:
        # - netloc: "owner"
        # - path: "/repo/path/to/file"

        owner = self.location  # This is the netloc part (owner)

        if not self.path or self.path == "/":
            raise ValueError("Invalid GitHub URI format - missing repo")

        # Split the path to get repo and file_path
        path_parts = self.path.lstrip("/").split("/")

        if len(path_parts) < 1:
            raise ValueError("Invalid GitHub URI format - missing repo")

        repo = path_parts[0]
        file_path = "/".join(path_parts[1:]) if len(path_parts) > 1 else ""

        return owner, repo, file_path

    def parse_sheets_components(self) -> tuple[str, str, Optional[str]]:
        """Extract spreadsheet_id, sheet_name, and range from Sheets URI"""
        if self.scheme != "sheets":
            raise ValueError("Not a Sheets URI")

        spreadsheet_id = self.location
        sheet_name = self.path.lstrip("/") if self.path else "Sheet1"

        # Parse range from query
        range_spec = None
        if self.query:
            params = dict(
                param.split("=") for param in self.query.split("&") if "=" in param
            )
            range_spec = params.get("range")

        return spreadsheet_id, sheet_name, range_spec

    def to_native_url(self) -> str:
        """Convert Siphon URI to native app URL for opening"""
        if self.scheme == "obsidian":
            # Convert to Obsidian app URL
            return f"obsidian://open?vault={self.location}&file={self.path.lstrip('/')}"

        elif self.scheme == "github":
            # Convert to GitHub web URL
            base = f"https://github.com/{self.location}"
            if self.path:
                # Determine if it's a file or directory
                base += f"/blob/main{self.path}"
            if self.fragment:
                base += f"#{self.fragment}"
            return base

        elif self.scheme == "sheets":
            # Convert to Google Sheets web URL
            spreadsheet_id, sheet_name, range_spec = self.parse_sheets_components()
            base = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            if sheet_name != "Sheet1":
                # Add sheet navigation (gid would need to be looked up)
                base += f"#gid=0"  # Simplified - would need sheet ID lookup
            return base

        elif self.scheme == "drive":
            # Convert to Google Drive web URL
            return f"https://drive.google.com/file/d/{self.location}/view"

        elif self.scheme in ["http", "https"]:
            # Already a web URL
            return self.raw_uri

        elif self.scheme == "file":
            # Return file path for system to handle
            return self.raw_uri

        else:
            # Default: return original URI
            return self.raw_uri

    def open_in_app(self) -> bool:
        """Open the URI in the appropriate application"""
        try:
            native_url = self.to_native_url()

            # Platform-specific opening
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", native_url], check=True)
            elif platform.system() == "Windows":
                subprocess.run(["start", native_url], shell=True, check=True)
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", native_url], check=True)
            else:
                return False

            return True
        except subprocess.CalledProcessError:
            return False

    def get_display_name(self) -> str:
        """Get a human-readable display name for this URI"""
        if self.scheme == "file":
            return Path(self.path).name

        elif self.scheme == "obsidian":
            note_name = Path(self.path).stem
            return f"{note_name} (Obsidian)"

        elif self.scheme == "github":
            owner, repo, file_path = self.parse_github_components()
            if file_path:
                return f"{Path(file_path).name} ({owner}/{repo})"
            else:
                return f"{owner}/{repo}"

        elif self.scheme == "sheets":
            spreadsheet_id, sheet_name, _ = self.parse_sheets_components()
            return f"{sheet_name} (Sheets)"

        elif self.scheme == "recording":
            return f"Recording {self.location}"

        elif self.scheme in ["http", "https"]:
            return self.location  # Domain name

        else:
            return self.raw_uri

    def is_file_based(self) -> bool:
        """Check if this URI represents a file-based resource"""
        return self.scheme in {"file", "obsidian", "github"}

    def is_web_based(self) -> bool:
        """Check if this URI represents a web-based resource"""
        return self.scheme in {"http", "https", "sheets", "drive"}

    def __str__(self) -> str:
        return self.raw_uri

    def __repr__(self) -> str:
        return f"SiphonURI('{self.raw_uri}')"


# Example usage and testing
if __name__ == "__main__":
    # Test various URI types
    uris = [
        SiphonURI.create_file_uri("/Users/brian/docs/notes.pdf"),
        SiphonURI.create_obsidian_uri("my-vault", "daily-notes/2024-06-16.md"),
        SiphonURI.create_github_uri("acesanderson", "Siphon", "ingestion/siphon.py"),
        SiphonURI.create_sheets_uri(
            "1BxiMVs0XRA5nFMRrOHP0mBBCH1cjYn6v", "Sheet1", "A1:C10"
        ),
        SiphonURI.create_recording_uri("2024-06-16T14:30:00Z"),
        SiphonURI.create_email_uri("msg123", "thread456"),
        SiphonURI.from_string("https://youtube.com/watch?v=abc123"),
    ]

    for uri in uris:
        print(f"URI: {uri}")
        print(f"Display: {uri.get_display_name()}")
        print(f"Native: {uri.to_native_url()}")
        print(f"File-based: {uri.is_file_based()}")
        print("---")

from Siphon.database.postgres.PGRES_siphon import get_siphon_by_hash, insert_siphon
from Siphon.data.extensions import extensions
import hashlib
from pathlib import Path


dir_path = Path(__file__).parent
asset_dir = dir_path / "assets"
asset_files = list(asset_dir.glob("*.*"))


# Our functions
def hash_file(filepath):
    """Generate SHA-256 hash of file contents"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def route_file(file_path: Path):
    """Route the file to the appropriate handler based on its extension."""
    ext = file_path.suffix.lower()
    for category, exts in extensions.items():
        if ext in exts:
            return category
    return "unknown"


def convert_markitdown(file_path: Path):
    """Convert a file using MarkItDown."""
    from markitdown import MarkItDown

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["markitdown"]:
        raise ValueError(f"File type not supported for MarkItDown: {file_path.suffix}")
    # Do the conversion
    md = MarkItDown()
    return md.convert(file_path)


def convert_raw(file_path: Path):
    """Convert raw files (CSV, JSON, etc.) to text."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["raw"]:
        raise ValueError(
            f"File type not supported for raw conversion: {file_path.suffix}"
        )
    # Implement raw conversion logic here
    with open(file_path, "r") as f:
        return f.read()


def convert_code(file_path: Path):
    """Convert code files to text."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["code"]:
        raise ValueError(
            f"File type not supported for code conversion: {file_path.suffix}"
        )
    # Implement code conversion logic here
    with open(file_path, "r") as f:
        return f.read()


def convert_audio(file_path: Path):
    """Convert audio/video files using Whisper."""
    from Siphon.ingestion.audio.audio import get_transcript

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["audio"]:
        raise ValueError(
            f"File type not supported for Whisper conversion: {file_path.suffix}"
        )
    output = get_transcript(file_path)
    return output


def convert_video(file_path: Path):
    """Convert video files to text."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["video"]:
        raise ValueError(
            f"File type not supported for video conversion: {file_path.suffix}"
        )
    # Implement video conversion logic here
    # Placeholder for actual video conversion implementation
    raise NotImplementedError("Video conversion not implemented yet.")


def convert_image(file_path: Path):
    """Convert image files using OCR."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["image"]:
        raise ValueError(
            f"File type not supported for OCR conversion: {file_path.suffix}"
        )
    from Siphon.ingestion.image.image import describe_image

    output = describe_image(file_path)
    return output


def convert_archive(file_path: Path):
    """Extract and convert archive files."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["archive"]:
        raise ValueError(
            f"File type not supported for archive conversion: {file_path.suffix}"
        )
    # Implement archive extraction logic here
    # Placeholder for actual archive extraction implementation
    raise NotImplementedError("Archive extraction not implemented yet.")


def convert_specialized(file_path: Path):
    """Convert specialized files (e.g., ePub, mobi)."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.suffix.lower() in extensions["specialized"]:
        raise ValueError(
            f"File type not supported for specialized conversion: {file_path.suffix}"
        )
    # Implement specialized file conversion logic here
    # Placeholder for actual specialized file conversion implementation
    raise NotImplementedError("Specialized file conversion not implemented yet.")


def retrieve_file_context(file_path: Path) -> str:
    category = route_file(file_path)
    """Convert a file based on its type."""
    output = ""
    match category:
        case "markitdown":
            output = convert_markitdown(file_path)
        case "raw":
            output = convert_raw(file_path)
        case "code":
            output = convert_code(file_path)
        case "audio":
            output = convert_audio(file_path)
        case "video":
            output = convert_video(file_path)
        case "image":
            output = convert_image(file_path)
        case "archive":
            output = convert_archive(file_path)
        case "specialized":
            output = convert_specialized(file_path)
        case "unknown":
            raise ValueError(f"Unknown file type for: {file_path}")
        case _:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    return output

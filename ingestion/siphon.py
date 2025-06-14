"""
Siphon is a collection of scripts that convert files to LLM context.
Identify file type, and then use the siphoning method appropriate (markitdown for lots of formats, whisper for audio/video formats)

# Design considerations
- cache all context by file hash (using postgres)
- add context markers - [IMAGE DESCRIPTION], [AUDIO TRANSCRIPT], [TABLE START/END]
"""

from Siphon.database.postgres.PGRES_siphon import insert_siphon, get_siphon_by_hash
from Siphon.data.ProcessedFile import ProcessedFile
from pathlib import Path
import hashlib, argparse

dir_path = Path(__file__).parent
asset_dir = dir_path / "assets"
asset_files = list(asset_dir.glob("*.*"))


extensions = {
    "raw": [".csv", ".json", ".xml", ".txt", ".md", ".yaml", ".yml", ".toml", ".ini"],
    "code": [
        ".py",
        ".js",
        ".html",
        ".css",
        ".java",
        ".cpp",
        ".c",
        ".go",
        ".rs",
        ".rb",
        ".php",
    ],
    "markitdown": [
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".pdf",
        ".msg",
        ".html",
        ".rtf",
    ],
    "audio": [
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
    ],
    "video": [
        ".mp4",
        ".avi",
        ".mov",
        ".webm",
        ".mkv",
    ],
    "image": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".svg",
        ".webp",
        ".ico",
    ],
    "archive": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "specialized": [".epub", ".mobi"],
}


# Our functions
def hash_file(filepath):
    """Generate SHA-256 hash of file contents"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def categorize(file_path: Path):
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
    from Chain import create_image_message, Model, Chain

    prompt_str = "Please describe this image in detail."
    imagemessage = create_image_message(file_path, prompt_str)

    model = Model("gpt")
    chain = Chain(model=model)
    response = chain.run(messages=[imagemessage])
    return response.content


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


def convert_file(file_path: Path):
    """Convert a file based on its type."""
    category = categorize(file_path)
    # Create hash and check cache here
    sha256 = hash_file(file_path)
    llm_context = get_siphon_by_hash(sha256)
    if llm_context:
        return llm_context
    # If not in cache, convert the file
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

    if output:
        abs_path = str(file_path.resolve())
        processed_file = ProcessedFile(
            sha256=sha256, abs_path=abs_path, llm_context=str(output)
        )
        insert_siphon(processed_file)
        return output


def main():
    parser = argparse.ArgumentParser(description="Siphon file to LLM context")
    parser.add_argument("file", type=str, help="Path to the file to convert")
    # parser.add_argument(
    #     "-l", "llm", action="store_true", help="Use LLM for conversion if applicable"
    # )
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    try:
        context = convert_file(file_path)
        print(f"Converted context for {file_path}:")
        print(context)
    except Exception as e:
        print(f"Error converting file {file_path}: {e}")


if __name__ == "__main__":
    main()

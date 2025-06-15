"""
Siphon is a collection of scripts that convert files to LLM context.
Identify file type, and then use the siphoning method appropriate (markitdown for lots of formats, whisper for audio/video formats)

# Design considerations
- cache all context by file hash (using postgres)
- add context markers - [IMAGE DESCRIPTION], [AUDIO TRANSCRIPT], [TABLE START/END]
"""

from Siphon.data.ProcessedContent import ProcessedContent, ProcessedURL, ProcessedFile
from Siphon.ingestion.file_context import retrieve_file_context
from Siphon.ingestion.online_context import retrieve_online_context
from pathlib import Path
import argparse
from typing import Literal


route = Literal["url", "file"]


def parse_input_data(input_data: str | Path) -> route:
    """
    Rourte as either online or file based on input data.
    """
    if isinstance(input_data, Path) or Path(input_data).exists():
        return "file"
    if input_data.startswith("http://") or input_data.startswith("https://"):
        return "url"
    else:
        raise ValueError(f"Invalid input data: {input_data}")


def create_siphon(input_data: str | Path) -> ProcessedContent:
    """
    Take input (filename, url, or otherwise) and return ProcessedContent.
    Accepts either a file path or a URL, str or Path.
    """
    route = parse_input_data(input_data)
    match route:
        case "file":
            input_data = str(input_data)
            context = retrieve_file_context(Path(input_data))
        case "url":
            context = retrieve_online_context(str(input_data))
    if not context:
        raise ValueError(f"Could not retrieve context for {input_data}")
    # create ProcessedContent object
    pass


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
        context = retrieve_file_context(file_path)
        print(f"Converted context for {file_path}:")
        print(context)
    except Exception as e:
        print(f"Error converting file {file_path}: {e}")


if __name__ == "__main__":
    main()

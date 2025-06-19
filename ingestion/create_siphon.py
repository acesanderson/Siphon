from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.URI import SiphonURI
from Siphon.data.Metadata import SiphonMetadata
from Siphon.data.SyntheticData import SyntheticData
from Siphon.ingestion.file_context import retrieve_file_context
from Siphon.ingestion.online_context import retrieve_online_context
from pathlib import Path
from typing import Literal


route = Literal["url", "file"]

# caching logic
"""
category = route_file(file_path)
# Create hash and check cache here
sha256 = hash_file(file_path)
llm_context = get_siphon_by_hash(sha256)
if llm_context:
    return llm_context
# If not in cache, convert the file
"""


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

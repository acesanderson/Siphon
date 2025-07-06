"""
This is the CLI entry point for Siphon.

Users can either provide a file path or a URL to retrieve the context.
Usage:
    python siphon_cli.py <file_or_url>

This script will determine if the input is a file path or a URL,
and then retrieve the context + store it from the specified source.
"""

from Siphon.main.siphon import siphon
from Siphon.data.URI import URI
from pydantic import BaseModel, Field
from typing import Literal, Optional
import argparse

class CLIParams(BaseModel):
    source: str = Field(..., description="Path to the file or URL to retrieve context from")
    return_type: Optional[Literal["m", "c", "s"]] = Field(
        default="s",
        description="Type of data to return: 'metadata', 'context', or 'synthetic_data'. Defaults to 'synthetic_data', i.e. a summary."
    )

    # flags
    persist: bool = Field(
        default=False, description="Persist the processed content to disk. Eventually this will be True by default."
    )
    llm: bool = Field(
        default=False, description="Use cloud LLM for conversion if applicable."
    )


def main():
    parser = argparse.ArgumentParser(description="Siphon file to LLM context")
    parser.add_argument("source", type=str, help="Path to the file to convert")
    parser.add_argument(
        "-l", "llm", action="store_true", help="Use cloud LLM for conversion if applicable"
    )
    parser.add_argument(
        "-p", "--persist", action="store_true", help="Persist the processed content to disk"
    )
    parser.add_argument(
        "-r",
        "--return_type",
        type=str,
        choices=["m", "c", "s"],
        default="s",
        help="Type of data to return: 'm' (metadata), 'c' (context), or 's' (synthetic data). Defaults to 'synthetic_data', i.e. a summary.",
    )

    args = parser.parse_args()
    query = CLIParams(**vars(args))
    source = args.source
    if not source:
        print(f"Need a source string.")
        return
    try:
        uri = URI.from_source(source)
        if uri:
            processedcontent = siphon(source)
        print(f"Converted context for {source}:")
        print(context)
    except Exception as e:
        print(f"Error converting source {source}: {e}")


if __name__ == "__main__":
    main()

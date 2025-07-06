"""
This is the CLI entry point for Siphon.

Users can either provide a file path or a URL to retrieve the context.
Usage:
    python siphon_cli.py <file_or_url>

This script will determine if the input is a file path or a URL,
and then retrieve the context + store it from the specified source.
"""

from pathlib import Path
import argparse
from Siphon.main.siphon import siphon

def main():
    parser = argparse.ArgumentParser(description="Siphon file to LLM context")
    parser.add_argument("source", type=str, help="Path to the file to convert")
    # parser.add_argument(
    #     "-l", "llm", action="store_true", help="Use cloud LLM for conversion if applicable"
    # )
    args = parser.parse_args()
    source = args.source
    if not source:
        print(f"Need a source string.")
        return
    try:
        context = siphon(source)
        print(f"Converted context for {source}:")
        print(context)
    except Exception as e:
        print(f"Error converting source {source}: {e}")


if __name__ == "__main__":
    main()

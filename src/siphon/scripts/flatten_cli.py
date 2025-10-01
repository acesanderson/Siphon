#!/usr/bin/env python3
"""
Flatten - CLI tool for converting GitHub repositories and local directories
into LLM-friendly XML format.

Usage:
    python Flatten.py .                                    # Flatten current directory
    python Flatten.py /path/to/directory                   # Flatten specific directory
    python Flatten.py https://github.com/owner/repo        # Flatten GitHub repository
"""

import argparse
import sys

from siphon.ingestion.github.flatten_directory import flatten_directory
from siphon.ingestion.github.flatten_url import flatten_github_repo


def main():
    """Main CLI entry point for the Flatten tool."""
    parser = argparse.ArgumentParser(
        description="Flatten a GitHub repo or local directory into LLM-friendly XML format",
        epilog="Examples:\n"
        "  %(prog)s .                                    # Current directory\n"
        "  %(prog)s /path/to/project                     # Specific directory\n"
        "  %(prog)s https://github.com/owner/repo        # GitHub repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "target",
        type=str,
        help="GitHub URL, directory path, or '.' for current directory",
    )

    args = parser.parse_args()
    target = args.target

    # Detect no input, if no args provided, show help
    # If no args provided, show help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        if target.startswith("https://github.com/"):
            # Process GitHub repository
            output = flatten_github_repo(target)
            print(output)
        else:
            # Process local directory (including ".")
            output = flatten_directory(target)
            print(output)

    except Exception as e:
        print(f"Error processing target '{target}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

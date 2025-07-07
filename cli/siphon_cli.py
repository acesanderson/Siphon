"""
This is the CLI entry point for Siphon.

Users can either provide a file path or a URL to retrieve the context.
Usage:
    python siphon_cli.py <file_or_url>

This script will determine if the input is a file path or a URL,
and then retrieve the context + store it from the specified source.
"""

from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams
import argparse


def main():
    parser = argparse.ArgumentParser(description="Siphon file to LLM context")
    parser.add_argument("source", type=str, help="Path to the file to convert")
    parser.add_argument(
        "-l",
        "--llm",
        action="store_true",
        help="Use cloud LLM for conversion if applicable",
    )
    parser.add_argument(
        "-p",
        "--persist",
        action="store_true",
        help="Persist the processed content to disk",
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
    args_dict = vars(args)
    query = CLIParams(
        source=args_dict["source"],
        return_type=args_dict["return_type"],
        persist=args_dict["persist"],
        llm=args_dict["llm"],
    )
    if query:
        response = siphon(query)
        print(response)


if __name__ == "__main__":
    main()

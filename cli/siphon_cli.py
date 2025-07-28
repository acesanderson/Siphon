"""
This is the CLI entry point for Siphon.

Think of this as `cat` for LLMs. A simple command-line interface to convert files or URLs into context for LLMs.

Users can either provide a file path or a URL to retrieve the context.
Usage:
    python siphon_cli.py <file_or_url>

This script will determine if the input is a file path or a URL,
and then retrieve the context + store it from the specified source.
"""

from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams
from Siphon.logs.logging_config import configure_logging
import argparse, logging, sys
from typing import TYPE_CHECKING

logger = configure_logging(
    level=logging.ERROR,
    console=True,
)


if TYPE_CHECKING:
    from Chain.message.imagemessage import ImageMessage


def grab_image_from_clipboard() -> tuple | None:
    """
    Attempt to grab image from clipboard; return tuple of mime_type and base64.
    """
    import os

    if "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ:
        print("Image paste not available over SSH.")
        return

    import warnings
    from PIL import ImageGrab
    import base64, io, sys

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress PIL warnings
        image = ImageGrab.grabclipboard()

    if image:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")  # type: ignore[reportCallIssue]
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        # Save for next query
        print("Image captured!")
        # Build our ImageMessage
        image_content = img_base64
        mime_type = "image/png"
        return mime_type, image_content
    else:
        print("No image detected.")
        sys.exit()


def create_image_message(
    combined_query: str, mime_type: str, image_content: str
) -> "ImageMessage | None":
    if not image_content or not mime_type:
        return
    role = "user"
    text_content = combined_query

    from Chain.message.imagemessage import ImageMessage

    imagemessage = ImageMessage(
        role=role,
        text_content=text_content,
        image_content=image_content,
        mime_type=mime_type,
    )
    return imagemessage


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
        choices=["c", "s"],
        default="s",
        help="Type of data to return: 'c' (context), or 's' (synthetic data). Defaults to 'synthetic_data', i.e. a summary.",
    )
    parser.add_argument(
        "-c",
        "--cache-options",
        type=str,
        choices=["u", "r"],
        help="Special cache flags: 'u' (uncached, do not save), or 'r' (recache, save again).",
    )
    parser.add_argument(
        "-i",
        "--image",
        action="store_true",
        help="Grab an image from the clipboard and use it as context.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print the output.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output raw markdown without formatting.",
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
        processed_content = siphon(query)
        output = f"# {processed_content.title}: {processed_content.id}\n\n{processed_content.summary}"
        if args.return_type:
            if args.return_type == "c":
                print(processed_content.context)
                sys.exit()
            if args.return_type == "s":
                print(processed_content.summary)
                sys.exit()
        if args.pretty:
            processed_content.pretty_print()
            sys.exit()
        if args.raw:
            print(output)
            sys.exit()
        else:
            from rich.markdown import Markdown
            from rich.console import Console

            console = Console()
            markdown = Markdown(output)
            console.print(markdown)
            sys.exit()


if __name__ == "__main__":
    main()

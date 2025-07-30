"""
Updated main/siphon.py with PostgreSQL cache integration
"""

from Siphon.data.URI import URI
from Siphon.data.Context import Context
from Siphon.data.SyntheticData import SyntheticData
from Siphon.cli.cli_params import CLIParams
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.database.postgres.PGRES_processed_content import (
    get_cached_content,
    cache_processed_content,
)
from Siphon.logs.logging_config import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Chain.message.imagemessage import ImageMessage

logger = get_logger(__name__)


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


def siphon(cli_params: CLIParams | str) -> ProcessedContent:
    """
    Siphon orchestrates the process of converting a source string (file path or URL).
    Now includes PostgreSQL caching for performance.
    """
    # Validate input
    if isinstance(cli_params, str):
        source = cli_params
        cache_options = "c"  # Default, cache it.
    elif isinstance(cli_params, CLIParams):
        source = cli_params.source
        cache_options = cli_params.cache_options
    else:
        raise TypeError(
            f"Expected a string or CLIParams object, got: {cli_params.__class__.__name__}"
        )

    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"Invalid source: {source}. Must be a valid file path or URL.")

    if cache_options == "c":
        logger.info(f"Checking cache for URI: {uri.uri}")
        try:
            cached_content = get_cached_content(uri.uri)
            if cached_content:
                logger.info(f"Cache HIT! Returning cached content")
                return cached_content
            else:
                logger.info(f"Cache MISS - no content found")
        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")

    # 3. Generate LLM context from the URI (retrieving text content)
    logger.info("Generating context from URI...")
    context = Context.from_uri(uri)

    # 4. Generate SyntheticData (post-processing)
    logger.info("Generating synthetic data...")
    synthetic_data = SyntheticData.from_context(context)

    # 5. Construct ProcessedContent object
    processed_content = ProcessedContent(
        uri=uri,
        llm_context=context,
        synthetic_data=synthetic_data,
    )

    if cache_options in ["c", "r"]:
        try:
            logger.info(f"Attempting to cache content for URI: {uri.uri}")
            result = cache_processed_content(processed_content)
            logger.info(f"Successfully cached with key: {result}")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    # 7. Return the processed content
    return processed_content

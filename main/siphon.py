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

logger = get_logger(__name__)


def siphon(cli_params: CLIParams | str) -> ProcessedContent:
    """
    Siphon orchestrates the process of converting a source string (file path or URL).
    Now includes PostgreSQL caching for performance.
    """
    # Validate input
    if isinstance(cli_params, str):
        source = cli_params
        use_cache = True  # Default to using cache for string inputs
    elif isinstance(cli_params, CLIParams):
        source = cli_params.source
        use_cache = not getattr(
            cli_params, "no_cache", False
        )  # Allow cache bypass via CLI flag
    else:
        raise TypeError(
            f"Expected a string or CLIParams object, got: {cli_params.__class__.__name__}"
        )

    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"Invalid source: {source}. Must be a valid file path or URL.")

    if use_cache:
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

    if use_cache:
        try:
            logger.info(f"Attempting to cache content for URI: {uri.uri}")
            result = cache_processed_content(processed_content)
            logger.info(f"Successfully cached with key: {result}")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    # 7. Return the processed content
    return processed_content

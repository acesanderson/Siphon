from Siphon.data.URI import URI
from Siphon.data.Context import Context
from Siphon.data.SyntheticData import SyntheticData
from Siphon.cli.cli_params import CLIParams
from Siphon.data.ProcessedContent import ProcessedContent


def siphon(cli_params: CLIParams | str) -> str:
    """
    Siphon orchestrates the process of converting a source string (file path or URL).
    Receives either a string (back-end request) or a CLIParams (user-driven request), and routes the flow accordingly.
    """
    # Validate input
    if isinstance(cli_params, str):
        source = cli_params
    elif isinstance(cli_params, CLIParams):
        source = cli_params.source
    else:
        raise TypeError("Expected a string or CLIParams object, got: {cli_params.__class__.__name__}")

    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"Invalid source: {source}. Must be a valid file path or URL.")
    # 2. Check against cache
    # if existing := db.get_by_id(content_id):
    #     return existing
    # 3. Generate LLM context from the URI (retrieving text content)
    context = Context.from_uri(uri)
    # 4. Generate SyntheticData (post-processing)
    synthetic_data = SyntheticData.from_context(context)
    # 5. Construct ProcessedContent object
    processed_content = ProcessedContent(
        uri=uri,
        llm_context=context,
        synthetic_data=synthetic_data,
    )
    # 5. Save to database
    # db.save(processed_content)
    # 6. Return the processed content
    # return processed_content
    return processed_content

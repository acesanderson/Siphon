"""
This is pseudocode for now, I am brainstorming on what the high level orchestration will actually look like.


7-6-2025:
- finalize Petrosian-local (i.e. not audio or image processing) siphon flow for:
    - source string -> URI -> metadata
        - should be able to see metadata objects for each URI type
    - source string -> URI -> llm_context
        - able to generate llm_context for any arbitrary source
- Connect AlphaBlue for local llm workflows
    - SiphonServer takes 
- 

"""

from Siphon.data.URI import URI
from Siphon.data.Metadata import Metadata
# from Siphon.data.SyntheticData import SyntheticData
from Siphon.cli.cli_params import CLIParams
# from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.ingestion.retrieve import retrieve_llm_context


def siphon(cli_params: CLIParams) -> Metadata:
    """
    Siphon orchestrates the process of converting a source string (file path or URL).
    Receives either a string (back-end request) or a CLIParams (user-driven request), and routes the flow accordingly.
    """
    source = cli_params.source
    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    if not uri:
        raise ValueError(f"Invalid source: {source}. Must be a valid file path or URL.")
    # 2. Check against cache
    # if existing := db.get_by_id(content_id):
    #     return existing
    # 3. Generate Metadata
    if uri:
        metadata = Metadata.from_uri(uri)
    # 5. Generate LLM context from the URI (retrieving text content)
    llm_context = retrieve_llm_context(uri)
    # 6. Generate SyntheticData (post-processing)
    # synthetic_data = SyntheticData.from_llm_context(llm_context)
    # 7. Construct ProcessedContent object
    # processed_content = ProcessedContent(
    #     uri=uri,
    #     ingested_at=int(time.time()),
    #     last_updated=int(time.time()),
    #     metadata=metadata,
    #     llm_context=llm_context,
    #     synthetic_data=synthetic_data,
    # )
    # 7. Save to database
    # db.save(processed_content)
    # 8. Return the processed content
    # return processed_content
    return llm_context

def CLI_handler():
    """
    If siphon function got a CLIParams object, then it will run the CLI flow.
    """
    pass

def string_handler():
    """
    If siphon function got a string, then it will run the string flow. More likely for back-end use cases.
    """
    pass

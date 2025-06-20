"""
This is pseudocode for now, I am brainstorming on what the high level orchestration will actually look like.
"""

from Siphon.data.URI import URI
from Siphon.data.ContentID import ContentID
from Siphon.data.Metadata import Metadata
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.ingestion.retrieve import retrieve_llm_context


def ingest_Siphon(source: str) -> ProcessedContent:
    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    # 2. Generate content_id
    content_id = ContentID.from_uri(uri)
    # 3. Check against cache
    if existing := db.get_by_id(content_id):
        return existing
    # 4. Generate Metadata
    metadata = Metadata.from_uri(uri)
    # 5. Generate LLM context from the URI (retrieving text content)
    llm_context = retrieve_llm_context(uri)
    # 6. Generate SyntheticData (post-processing)
    synthetic_data = SyntheticData.from_llm_context(llm_context)
    # 7. Construct ProcessedContent object
    processed_content = ProcessedContent(
        content_id=content_id,
        uri=uri,
        ingested_at=int(time.time()),
        last_updated=int(time.time()),
        llm_context=llm_context,
        synthetic_data=synthetic_data,
        metadata=metadata,
    )
    # 7. Save to database
    db.save(processed_content)
    # 8. Return the processed content
    return processed_content


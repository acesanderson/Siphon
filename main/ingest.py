"""
This is pseudocode for now, I am brainstorming on what the high level orchestration will actually look like.

1. generate URI (source -> URI)
2. create context from URI (URI -> llm_context)
3. post-process (URI + llm_context -> ProcessedContent)
4. save to database
5. return ProcessedContent object
"""
from Siphon.data.URI import URI
from Siphon.data.ContentID import ContentID
from Siphon.data.Metadata import Metadata
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.ProcessedContent import ProcessedContent


def ingest_Siphon(source: str) -> ProcessedContent:
    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    # 2. Check against cache
    content_id = ContentID.from_uri(uri)  # or UUID generation logic
    if existing := db.get_by_id(content_id):
        return existing
    # 3. Generate Metadata
    metadata = Metadata.from_uri(uri)
    # 4. Generate LLM context from the URI (retrieving text content)
    llm_context = generate_context(uri)
    # 5. Generate SyntheticData (post-processing)
    synthetic_data = SyntheticData.from_llm_context(llm_context)
    # 5. Save to database
    await db.save(processed_content)
    # 6. Return the processed content
    return processed_content


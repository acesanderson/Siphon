"""
This is pseudocode for now, I am brainstorming on what the high level orchestration will actually look like.

1. generate URI (source -> URI)
2. create context from URI (URI -> llm_context)
3. post-process (URI + llm_context -> ProcessedContent)
4. save to database
5. return ProcessedContent object
"""

async def ingest_Siphon(source: str) -> ProcessedContent:
    # 1. Parse source into structured URI
    uri = URI.from_source(source)
    # 2. Check against cache
    cache_key = generate_hash(uri)  # or UUID generation logic
    if existing := await db.get_by_id(cache_key):
        return existing
    # 3. Generate LLM context from the URI
    llm_context = await generate_context(uri)
    # 4. Post-process into final content object
    processed_content = await post_process(uri, llm_context, id=cache_key)
    # 5. Save to database
    await db.save(processed_content)
    # 6. Return the processed content
    return processed_content


# Siphon

An evolution of Leviathan, with the same principles:
- we ingest the world's information
- we create a RAG system for work docs and other files
- we flexibly turn any media into text based LLM context
- we help ourselves find files, connect ideas
- we help LLMs do the same through dedicated MCP servers

Here are the various input sources:

## File Context
-  raw: markdown, text, yaml, json, and other files that can be parsed as text.
-  docs: Microsoft Word documents (use MarkItDown).
-  audio: Audio parsing + record.
-  image: Image parsing and OCR.
-  video: Video parsing.

## Online Context
-  articles: Leviathan-style url parsing.
-  youtube: Leviathan-style YouTube parsing.
-  github: GitHub parsing.
-  email: Email parsing (forwarded to a specific address).

## Chronjob
-  downloads: Chronjob to parse Downloads folder.
-  googledrive: Google Drive parsing.
-  obsidian: Chronjob to parse Obsidian vault.

# Siphon Architecture
## Databases
- postgres: all of the data (expressed as ProcessedFile type)
- chroma: three tiered vector store
    - file descriptions (llm generated)
    - file summaries (llm generated)
    - chunks (within documents)
- neo4j: start with named entities

## System architecture
- postgres, chroma: Caruana server
- transcription server, ollama: AlphaBlue
- petrosian: client

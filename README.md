# Siphon

An evolution of Leviathan, with the same principles:
- we ingest the world's information
- we create a RAG system for work docs and other files
- we flexibly turn any media into text based LLM context
- we help ourselves find files, connect ideas
- we help LLMs do the same through dedicated MCP servers

## Data sources
### Command line
- docs (MSFT, pdf, etc.)
- audio (either recorded on the spot or from a file)
- video
- images
### Automated / Chronjob
- Obsidian vault
    - daily notes (and todos thereof)
- Downloads folder
- GitHub repos
### Online
- Youtube videos
- Articles / websites
- Google Sheets
- Emails (forwarded to a specific address)

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

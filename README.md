⠋ claude-sonnet-4-20250514 | [0/0] ✓ claude-sonnet-4-20250514 | [0/0]  | (35.1s)
# Siphon

A unified content ingestion and processing pipeline that transforms any source (files, URLs, multimedia) into structured, searchable, LLM-ready content with AI-generated enrichments.

## Features

- **Universal Content Ingestion**: Process files (documents, audio, video, images), URLs (YouTube, GitHub, articles), and cloud sources (Google Drive)
- **Intelligent Content Processing**: Extract text from any format using specialized handlers for each content type
- **AI-Powered Enrichment**: Generate titles, descriptions, summaries, topics, and entities using local or cloud LLMs
- **Robust Caching System**: PostgreSQL-backed cache with SQLite fallback for offline operation
- **CLI and Server Modes**: Use as a command-line tool or deploy as a FastAPI server
- **Extensible Architecture**: Modular design supporting easy addition of new content sources and processors

## Installation

```bash
pip install -e .
```

### System Dependencies

For audio processing:
```bash
# macOS
brew install portaudio ffmpeg

# Ubuntu/Debian
sudo apt-get install portaudio19-dev ffmpeg
```

### Environment Variables

```bash
export POSTGRES_PASSWORD="your_postgres_password"
export GITHUB_TOKEN="your_github_token"  # For GitHub repository processing
export OPENAI_API_KEY="your_openai_key"  # For cloud-based processing
```

## Quick Start

### Command Line Usage

```python
# Process a local file
siphon document.pdf

# Process a YouTube video
siphon https://www.youtube.com/watch?v=VIDEO_ID

# Process a GitHub repository
siphon https://github.com/owner/repo

# Use cloud LLM for processing
siphon audio.mp3 --llm

# Get raw context without enrichment
siphon document.docx --return_type c

# Pretty print output
siphon article_url --pretty
```

### Python API

```python
from Siphon import siphon
from Siphon.cli.cli_params import CLIParams

# Process content programmatically
params = CLIParams(source="path/to/file.pdf")
processed_content = siphon(params)

print(f"Title: {processed_content.title}")
print(f"Summary: {processed_content.summary}")

# Display formatted output
processed_content.pretty_print()
```

### Server Mode

```python
# Start the FastAPI server
from Siphon.api.server.run import main
main()

# Or use the client
from Siphon.api.client.siphon_client import SiphonClient

client = SiphonClient()
# Process audio/video/images remotely
result = client.request_context_call(context_call)
```

## Project Structure

```
Siphon/
├── main/siphon.py              # Core orchestration logic
├── cli/                        # Command-line interface
├── api/                        # FastAPI server and client
├── data/                       # Core data models (URI, Context, ProcessedContent)
├── ingestion/                  # Content retrieval and processing
│   ├── audio/                  # Audio transcription (local + cloud)
│   ├── image/                  # Image description (OCR + vision models)
│   ├── youtube/                # YouTube transcript processing
│   ├── github/                 # Repository flattening
│   └── article/                # Web article extraction
├── context/classes/            # Source-specific context processors
├── uri/classes/                # URI parsing and validation
├── synthetic_data/classes/     # AI enrichment generators
├── database/                   # PostgreSQL + SQLite caching
├── enrich/                     # AI-powered content enhancement
└── tests/                      # Comprehensive test suite
```

## Configuration

### Database Setup

Siphon automatically creates PostgreSQL tables and handles connection fallback:

```python
# Configure cache behavior
params = CLIParams(
    source="content.pdf",
    cache_options="c"  # 'c' (cache), 'u' (uncached), 'r' (recache)
)
```

### Audio Processing

Choose between local (private) or cloud-based transcription:

```python
# Local processing with Whisper + speaker diarization
processed = siphon(CLIParams(source="meeting.mp3"))

# Cloud processing with OpenAI
processed = siphon(CLIParams(source="meeting.mp3", llm=True))
```

## Supported Content Types

| Type | Extensions | Features |
|------|------------|----------|
| **Documents** | `.pdf`, `.docx`, `.pptx`, `.xlsx` | MarkItDown processing |
| **Audio** | `.mp3`, `.wav`, `.m4a`, `.ogg` | Transcription + diarization |
| **Images** | `.jpg`, `.png`, `.gif`, `.svg` | OCR + vision description |
| **Video** | `.mp4`, `.avi`, `.mov`, `.webm` | Planned audio extraction |
| **Text** | `.txt`, `.md`, `.csv`, `.json` | Direct processing |
| **Code** | `.py`, `.js`, `.html`, `.css` | Syntax-aware handling |
| **YouTube** | Video URLs | Transcript + metadata |
| **GitHub** | Repository URLs | Flatten to XML structure |
| **Articles** | Web URLs | Clean text extraction |
| **Google Drive** | Docs/Sheets/Slides | Planned integration |

## Contributing

1. **Add New Content Sources**: Implement URI, Context, and SyntheticData classes following the pattern
2. **Extend Processing**: Add handlers in `ingestion/` for new content types
3. **Improve AI**: Customize prompts in `synthetic_data/classes/` for source-specific enrichment
4. **Testing**: Run `pytest tests/` - comprehensive integration tests included

## License

MIT License - see LICENSE file for details

---

*Transform any content into structured, searchable knowledge with Siphon's intelligent processing pipeline.*
None

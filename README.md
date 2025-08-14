# Siphon

Siphon transforms any content source into structured, searchable, LLM-ready knowledge while you retain complete control over your data. Built for the age of AI agents, designed for minds that work in parallel.

## Philosophy

In the age of AI, human cognitive work is shifting to a higher altitude—managing context, connecting ideas, and making strategic decisions on the fly. Yet we're still trapped in fragmented tools with inconsistent search, scattered across Outlook, Google Drive, Slack, and dozens of other silos.

Siphon operates on four core principles:

1. **Everything is LLM context** — The process of converting any data source into usable context should be frictionless
2. **Retention vs. recall** — Save everything, optimize for retrieval. Embrace the chaos of an arbitrary corpus rather than forcing hierarchical organization
3. **Frictionless context engineering** — Assembling the right context for LLM tasks should be effortless
4. **Optimize for human efficiency** — Use AI to eliminate information silos and accelerate knowledge work

## What Siphon Does

**Process once, query forever.** Siphon converts any content source into structured, cached knowledge:

```bash
# Ingest anything
siphon quarterly-strategy.pdf
siphon https://www.youtube.com/watch?v=xyz  
siphon https://github.com/company/repo
siphon podcast.m4a
siphon competitive-analysis.pptx

# Get what you need
siphon document.pdf --return_type s    # Summary for quick scanning
siphon audio.mp3 --return_type c       # Full context for LLM input
```

Every source becomes a **ProcessedContent** object with:
- **Raw LLM context** — Clean, structured text ready for any AI model
- **AI-generated enrichments** — Searchable titles, descriptions, and summaries
- **Source-specific metadata** — YouTube view counts, GitHub stars, document authors
- **Persistent caching** — Process once, access instantly

## The Siphon Advantage

### Universal Ingestion Engine
11 source types supported out of the box:

| **Content Type** | **Examples** | **What You Get** |
|------------------|--------------|------------------|
| **Documents** | `.pdf`, `.docx`, `.pptx`, `.xlsx` | MarkItDown processing with preserved structure |
| **Audio/Video** | `.mp3`, `.wav`, `.m4a`, `.mp4` | Transcription + speaker diarization |
| **Code** | GitHub repos, local projects | Flattened XML structure for LLM analysis |
| **Web Content** | Articles, YouTube videos | Clean text + rich metadata |
| **Visual** | `.jpg`, `.png`, images | OCR + AI-powered descriptions |

### Intelligent Caching
PostgreSQL-backed cache with SQLite fallback ensures you never process the same content twice:

```bash
siphon important-doc.pdf        # First run: full processing
siphon important-doc.pdf        # Subsequent runs: instant retrieval
```

### Research Synthesis
Multi-document analysis powered by async LLM processing:

```bash
research_cli.py "Datadog's AI strategy" --dir ./competitive-intel/
# Analyzes entire directory, extracts relevant insights, synthesizes findings
```

## Quick Start

### Installation
```bash
pip install -e .

# System dependencies for audio processing
brew install portaudio ffmpeg  # macOS
# OR
sudo apt-get install portaudio19-dev ffmpeg  # Ubuntu
```

### Environment Setup
```bash
export POSTGRES_PASSWORD="your_postgres_password"
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_key"  # Optional: for cloud processing
```

### Basic Usage

```bash
# Process a document (local processing by default)
siphon strategy-doc.pdf

# Get YouTube transcript with metadata
siphon "https://youtube.com/watch?v=abc123"

# Analyze GitHub repository
siphon "https://github.com/company/important-repo"

# Audio transcription with speaker identification
siphon meeting-recording.m4a        # Local processing (secure by default)
siphon meeting-recording.m4a --llm  # Cloud processing (when explicitly opted-in)

# Research synthesis across multiple sources
research_cli.py "competitive AI positioning" --dir ./research-docs/
```

## Data Security & Privacy

### Local-First Architecture
Siphon processes sensitive content locally by default:
- **Local LLMs** — Use Ollama, LM Studio, or other local inference engines
- **On-premises processing** — Audio transcription, document parsing, and analysis run locally
- **No cloud uploads** — Proprietary data never leaves your infrastructure unless explicitly opted-in

### Cloud Processing (Opt-In Only)
For non-sensitive content, cloud LLMs can be enabled:
```bash
# Explicit opt-in required for cloud processing
siphon public-content.pdf --llm
siphon youtube-video.mp4 --llm  # OK for public content
```

### Data Classification
Built-in safeguards for handling different data types:
- **Proprietary documents** — Always processed locally
- **Public content** — User choice of local or cloud processing
- **Personal content** — Local processing recommended
- **Encrypted storage** — All cached content encrypted at rest

## Advanced Workflows

### Competitive Intelligence Pipeline
```bash
# Gather intelligence sources (local processing for proprietary data)
siphon competitor-earnings-call.mp3        # Local transcription
siphon industry-analysis.pdf               # Local processing
siphon https://youtube.com/watch?v=product-demo --llm  # Public content, cloud OK

# Synthesize insights (local LLM recommended for strategic analysis)
research_cli.py "competitive AI strategy and market positioning"
```

### Meeting Intelligence
```bash
# Process all-hands recording (always local for internal meetings)
siphon all-hands-january.m4a

# Get quick summary
siphon all-hands-january.m4a --return_type s

# Use full context for follow-up analysis
siphon strategy-followup.docx
# Both automatically cached and ready for cross-referencing
```

## Architecture: Built for Scale

### Factory Pattern Design
Every source type implements a consistent interface:
- **URI parsing** — Unified identification system
- **Context extraction** — Source-specific processing logic  
- **Metadata enrichment** — Relevant metadata per source type
- **Synthetic data generation** — AI-powered titles, descriptions, summaries

### Database Strategy
- **PostgreSQL** — Primary cache with full-text search and JSONB queries
- **SQLite fallback** — Offline operation when PostgreSQL unavailable
- **Automatic sync** — Seamless failover and recovery

### Processing Pipeline
```
Source → URI → Context → Synthetic Data → ProcessedContent → Cache
```

Every step is modular, testable, and extensible.

## The Sourdough Vision

*"Like sourdough starter, knowledge needs regular feeding and maintenance to stay alive and valuable."*

**Coming soon:** Auto-maintaining knowledge bases that:
- **Continuously curate** relevant content for specific research topics
- **Intelligent pruning** — Remove outdated information, retain evergreen insights  
- **Contextual summarization** — Always-current strategic snapshots
- **User feedback loops** — Learn your priorities through interaction

Example sourdough starter: Maintain a living intelligence base on "Datadog's AI strategy" that automatically incorporates new earnings calls, product announcements, and competitive moves.

## Integration Ecosystem

### CLI Power User
```bash
# Pipe to your LLM tools
siphon document.pdf --return_type c | llm "summarize key decisions"

# Batch processing
find ./docs -name "*.pdf" -exec siphon {} \;
```

### Python API
```python
from Siphon import siphon
from Siphon.cli.cli_params import CLIParams

# Programmatic processing
content = siphon(CLIParams(source="important-doc.pdf"))
print(f"Title: {content.title}")
print(f"Summary: {content.summary}")

# Access raw context for LLM prompts
llm_context = content.context
```

### FastAPI Server
Deploy Siphon as a service for audio/video processing, image analysis, and content enrichment.

## Production Features

### Security & Privacy
- **Local processing by default** — Keep sensitive data on your infrastructure
- **Explicit cloud opt-in** — Use `--llm` flag only when appropriate for non-sensitive content
- **Comprehensive caching** — Never re-process the same content
- **Encrypted storage** — All cached data encrypted at rest
- **Audit logging** — Track all processing operations and data flows

### Observability
- **Comprehensive logging** — Track all processing operations
- **Cache statistics** — Monitor storage usage and hit rates
- **Fallback monitoring** — Visibility into offline operation

### Extensibility
Adding new source types is straightforward:
1. Implement `URI`, `Context`, and `SyntheticData` classes
2. Add source-specific processing logic
3. Register with the factory system

## Why This Matters

We're building toward a future where:
- **Agents handle routine work** — You focus on strategy and creativity
- **Context is everything** — The right information at the right time drives decisions
- **Knowledge compounds** — Your accumulated insights become your competitive advantage
- **You own your data** — No vendor lock-in, no privacy compromises

Siphon prepares you for this future by making knowledge retention effortless and recall instantaneous.

## Contributing

Siphon is designed for extensibility. Whether you're adding support for new content types, improving AI processing, or building workflow integrations, we welcome contributions.

Key areas for development:
- **New source types** — Slack, email, Notion, etc.
- **Enhanced AI processing** — Better summarization, entity extraction, topic modeling
- **Integration layers** — MCP servers, agent frameworks, workflow tools

## License

MIT License — Use it, modify it, own it.

---

*Transform any content into structured knowledge. Build your personal intelligence infrastructure. Prepare for the agent future.*

**Ready to own your knowledge?**

```bash
pip install -e .
siphon your-first-document.pdf
```

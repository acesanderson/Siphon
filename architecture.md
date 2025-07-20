siphon/
├── __init__.py
├── main.py                       # Entry point (calls into CLI or orchestrator)

# ───────────── Pipeline Core ─────────────
├── pipeline/                     # Core base classes + strategy orchestrator
│   ├── __init__.py
│   ├── base.py                   # PipelineBase (abstract: run(), steps(), etc.)
│   ├── steps.py                  # Shared enrichment / parsing logic (e.g., summarize(), title())
│   ├── run_pipeline.py           # Orchestration logic for CLI + server
│   └── errors.py                 # Custom exceptions

# ───────────── Processed Content Abstraction ─────────────
models /
- init
- data_models /
     URI
     Context
     SyntheticData
     ProcessedContent
- types /
     SourceType
     Extensions
     URISchemes



├── model/                        # Atomic unit of the system
│   ├── __init__.py
│   ├── data_models /             # URI (with SourceType routing, validation)
|   │   ├── URI.py                    # URI (with SourceType routing, validation)
│   ├── Context.py                # Base class for Metadata, common timestamps
├   │   ├── SyntheticData.py          # SyntheticData (summaries, tags, etc.)
│   └── ProcessedContent.py       # ProcessedContent (URI + Metadata + SyntheticData)


# ───────────── Domain Module ─────────────
├── audio/                        # as example
│   ├── __init__.py
│   ├── audio_uri.py              # URI (with SourceType routing, validation)
│   ├── audio_context.py          # URI (with SourceType routing, validation)
│   ├── audio_synthetic_data.py   # URI (with SourceType routing, validation)
│   ├── ingestion/
│   │   └── retrieve_audio.py




# ───────────── Domain Modules ─────────────
├── domains/
│   ├── __init__.py               # Registers all known domains (if using registry)
│   ├── audio/
│   │   └── ...
│   ├── github/
│   │   └── ...
│   ├── youtube/
│   │   └── ...
│   ├── email/
│   │   └── ...
│   ├── obsidian/
│   │   └── ...
│   └── todo/
│       └── ...

# ───────────── Registry / Reflection (Optional) ─────────────
├── registry/
│   ├── __init__.py
│   ├── metadata_registry.py      # SourceType → Metadata class
│   ├── pipeline_registry.py      # SourceType → Pipeline class

# ───────────── CLI / Server Interfaces ─────────────
├── cli/
│   ├── siphon_cli.py             # CLI entry point (argparse)
│   └── cli_params.py             # Parameter models
├── server/
│   ├── siphon_server.py          # FastAPI (or Flask) API for remote ingestion
│   └── routes/                   # Route logic
│       └── ingest.py

# ───────────── Database Adapters ─────────────
├── storage/
│   ├── postgres_adapter.py       # save_to_postgres(ProcessedContent)
│   ├── chroma_adapter.py         # embed + store in ChromaDB
│   ├── neo4j_adapter.py          # store + index relationships
│   └── scheduler/                # For cron/daemon integration
│       └── obsidian_sync.py      # Obsidian vault → ProcessedContent

# ───────────── Tests / Fixtures ─────────────
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   └── test_pipeline/
│       ├── test_file.py
│       ├── test_obsidian.py
│       └── ...

# ───────────── Docs / Misc ─────────────
├── docs/
│   └── architecture.md
├── README.md
├── requirements.txt
└── pyproject.toml

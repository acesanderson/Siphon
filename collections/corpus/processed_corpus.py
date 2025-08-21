"""
ProcessedCorpus - Lightweight wrapper around collections of ProcessedContent objects

Provides convenience functions for managing and constructing ProcessedContent. To query a ProcessedCorpus, you should attach it to a SiphonQuery object.

A ProcessedCorpus can be constructed from a CorpusFactory, which can take various sources:
- Entire library of ProcessedContent from the database (DatabaseCorpus)
- Files in a directory (e.g., markdown, PDFs)
- List of URLs (e.g., YouTube, GitHub, articles)
- Content tagged with specific tags (not yet implemented)
- User-defined queries (not yet implemented) -- i.e. a SiphonQuery object
- Existing list of ProcessedContent objects
- TBD

A ProcessedCorpus, on initialization, will also have access to the following (either pre-existing for persistent, or created on-the-fly for in-memory):
- A lightweight in-memory representation of the corpus
- a vector store for similarity search (TBD)
- a graph representation of the corpus (TBD)
- NER, topic modeling, and other NLP features (TBD)
- Automatic summarization of content (TBD)
- Automatic tagging and categorization (TBD)

## Architecture

We define an abstract base class `ProcessedCorpus` that provides a rich interface.

We then implement:
- DatabaseCorpus (which uses pgres for specific queries, and leverages persistent Chroma and Neo4j databases, as well as library-wide AI tagging etc.)
- InMemoryCorpus (which is an in-memory set of ProcessedContent objects, with ephemeral chroma and networkx instead of neo4j)

These would use the same interface, but have different implementations for the underlying storage and retrieval mechanisms.

We then have a `CorpusFactory` that provides methods to create the appropriate corpus type based on the source:
"""

from collections.abc import Iterable
from abc import ABC, abstractmethod
from pathlib import Path

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.types.SourceType import SourceType
from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams


class ProcessedCorpus(ABC):
    """Abstract interface - all corpus types look the same to SiphonQuery."""

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __iter__(self): ...  # For when you DO need to iterate

    # ============================================================================
    # Metadata - Basic information about the corpus
    # ============================================================================

    # ============================================================================
    # Synthetic Data - Automatically generated metadata like summaries, tags, etc.
    # ============================================================================

    # ============================================================================
    # Constructors - Create corpus from various sources
    # ============================================================================

    # ============================================================================
    # Collection Management - Add/Remove operations
    # ============================================================================

    @abstractmethod
    def add(self, content: ProcessedContent) -> None:
        """Add ProcessedContent to the corpus."""
        ...

    @abstractmethod
    def remove(self, content: ProcessedContent) -> None:
        """Remove ProcessedContent from the corpus."""
        ...

    @abstractmethod
    def remove_by_uri(self, uri: str) -> bool:
        """
        Remove content by URI string.

        Returns:
            True if content was found and removed, False otherwise
        """
        ...

    # ============================================================================
    # View Operations - Different representations of the corpus
    # ============================================================================

    @abstractmethod
    def snapshot(self) -> str:
        """
        Get high-level overview (titles + descriptions) for quick scanning.
        Perfect for getting the gist of the corpus without full context.
        """
        ...

    # ============================================================================
    # Utility Methods
    # ============================================================================

    @abstractmethod
    def __len__(self) -> int:
        """Return number of items in corpus."""
        ...

    @abstractmethod
    def __contains__(self, content: ProcessedContent) -> bool:
        """Check if content is in corpus."""
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if corpus is empty."""
        return len(self.corpus) == 0

    @abstractmethod
    def get_source_type_counts(self) -> dict[SourceType, int]:
        """Get count of content by source type."""
        ...

    @abstractmethod
    def pretty_print(self) -> None:
        """Display corpus in a beautiful, structured format."""
        ...


class DatabaseCorpus(ProcessedCorpus):
    """
    Corpus backed by a persistent database (e.g., Postgres, Neo4j).
    Provides efficient querying and storage for large datasets.
    """

    # Implementation details would go here, including methods for querying,
    # adding/removing content, and any database-specific optimizations.
    pass


class InMemoryCorpus(ProcessedCorpus):
    """
    Corpus stored in memory, suitable for ephemeral use cases.
    Provides fast access and manipulation of ProcessedContent objects.
    Ideal for testing, prototyping, and small datasets.
    """

    def __init__(self, source: str, corpus: list[ProcessedContent] = None):
        """
        Initialize an in-memory corpus.

        Args:
            source: Identifier for the source of the corpus (e.g., "urls", "dir")
            corpus: Optional list of ProcessedContent objects to initialize with
        """
        self.source = source
        self.corpus = corpus if corpus is not None else []

    # Implementation of abstract methods from ProcessedCorpus
    def __len__(self) -> int:
        """Return the number of items in the corpus."""
        ...

    def __contains__(self, content: ProcessedContent) -> bool:
        """Check if a ProcessedContent object is in the corpus."""
        ...

    def is_empty(self) -> bool:
        """Check if the corpus is empty."""
        ...

    def get_source_type_counts(self) -> dict[SourceType, int]:
        """
        Get a count of content items by their source type.

        Returns:
            Dictionary mapping SourceType to count of items
        """
        counts = {}
        for content in self.corpus:
            sourcetype = content.uri.sourcetype
            counts[sourcetype] = counts.get(sourcetype, 0) + 1
        return counts

    def snapshot(self) -> str:
        if not self.corpus:
            return "Empty corpus"

        snapshot_lines = [f"Corpus Snapshot ({len(self.corpus)} items)"]
        snapshot_lines.append("=" * 50)

        for i, content in enumerate(self.corpus, 1):
            title = content.title or f"Content from {content.uri.sourcetype.value}"
            description = content.description or "No description available"

            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."

            snapshot_lines.append(f"{i}. {title}")
            snapshot_lines.append(f"   {description}")
            snapshot_lines.append("")

        return "\n".join(snapshot_lines)

    # Specific to InMemoryCorpus
    def text(self) -> str:
        """
        Get full context text from all content in corpus.
        Suitable for LLM consumption or detailed analysis.
        """
        if not self.corpus:
            return ""

        text_sections = []
        for content in self.corpus:
            section = [
                f"=== {content.title or 'Untitled'} ===",
                f"Source: {content.uri.uri}",
                f"Type: {content.uri.sourcetype.value}",
                "",
                content.context,
                "\n" + "=" * 80 + "\n",
            ]
            text_sections.append("\n".join(section))

        return "\n".join(text_sections)

    def __iter__(self) -> Iterable[ProcessedContent]:
        """Allow iteration over corpus content."""
        return iter(self.corpus)


class CorpusFactory:
    """Factory for creating the right corpus implementation."""

    @staticmethod
    def from_library() -> "DatabaseCorpus":
        """Create database-backed corpus for entire library."""
        return DatabaseCorpus()

    @staticmethod
    def from_directory(
        directory_path: str | Path, pattern: str = "*"
    ) -> "InMemoryCorpus":
        """Create in-memory corpus from directory files."""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = list(directory.glob(pattern))
        corpus_items = []

        for file_path in files:
            try:
                cli_params = CLIParams(source=str(file_path))
                processed_content = siphon(cli_params)
                corpus_items.append(processed_content)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return InMemoryCorpus(corpus_items)

    @staticmethod
    def from_url_list(urls: list[str]) -> "InMemoryCorpus":
        """Create in-memory corpus from URL list."""
        corpus_items = []
        for url in urls:
            try:
                cli_params = CLIParams(source=url)
                processed_content = siphon(cli_params)
                corpus_items.append(processed_content)
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        return InMemoryCorpus(corpus_items)

    @staticmethod
    def from_processed_content_list(
        content_list: list[ProcessedContent],
    ) -> "InMemoryCorpus":
        """Create in-memory corpus from existing content."""
        return InMemoryCorpus(content_list)

    @staticmethod
    def from_tag(tag: str) -> "DatabaseCorpus":
        """Create database-backed corpus filtered by tag."""
        # This would use database queries
        raise NotImplementedError("Tag-based corpus construction not yet implemented")

"""
SiphonCorpus - Lightweight wrapper around collections of ProcessedContent objects

Provides convenience functions for managing and constructing ProcessedContent. To query a SiphonCorpus, you should attach it to a SiphonQuery object.

A SiphonCorpus can be constructed from a CorpusFactory, which can take various sources:
- Entire library of ProcessedContent from the database (DatabaseCorpus)
- Files in a directory (e.g., markdown, PDFs)
- List of URLs (e.g., YouTube, GitHub, articles)
- Content tagged with specific tags (not yet implemented)
- User-defined queries (not yet implemented) -- i.e. a SiphonQuery object
- Existing list of ProcessedContent objects
- TBD

A SiphonCorpus, on initialization, will also have access to the following (either pre-existing for persistent, or created on-the-fly for in-memory):
- A lightweight in-memory representation of the corpus
- a vector store for similarity search (TBD)
- a graph representation of the corpus (TBD)
- NER, topic modeling, and other NLP features (TBD)
- Automatic summarization of content (TBD)
- Automatic tagging and categorization (TBD)

## Architecture

We define an abstract base class `SiphonCorpus` that provides a rich interface.

We then implement:
- DatabaseCorpus (which uses pgres for specific queries, and leverages persistent Chroma and Neo4j databases, as well as library-wide AI tagging etc.)
- InMemoryCorpus (which is an in-memory set of ProcessedContent objects, with ephemeral chroma and networkx instead of neo4j)

These would use the same interface, but have different implementations for the underlying storage and retrieval mechanisms.

We then have a `CorpusFactory` that provides methods to create the appropriate corpus type based on the source:
"""

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.types.SourceType import SourceType
from Siphon.database.postgres.PGRES_connection import get_db_connection
from psycopg2.extras import RealDictCursor
from typing import override
from collections.abc import Iterator
from abc import ABC, abstractmethod
from pathlib import Path


class SiphonCorpus(ABC):
    """Abstract interface - all corpus types look the same to SiphonQuery."""

    # Collection Management
    @abstractmethod
    def add(self, content: ProcessedContent) -> None: ...

    @abstractmethod
    def remove(self, content: ProcessedContent) -> None: ...

    @abstractmethod
    def remove_by_uri(self, uri: str) -> bool: ...

    # Iteration & Access
    @abstractmethod
    def __iter__(self) -> Iterator[ProcessedContent]: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __contains__(self, content: ProcessedContent) -> bool: ...

    # Query Interface (returns new corpus for chaining)
    @abstractmethod
    def filter_by_source_type(self, source_type: SourceType) -> "SiphonCorpus": ...

    @abstractmethod
    def filter_by_date_range(self, start_date, end_date) -> "SiphonCorpus": ...

    @abstractmethod
    def filter_by_tags(self, tags: list[str]) -> "SiphonCorpus": ...

    # Metadata & Views
    @abstractmethod
    def snapshot(self) -> str: ...

    @abstractmethod
    def get_source_type_counts(self) -> dict[SourceType, int]: ...

    @abstractmethod
    def is_empty(self) -> bool: ...

    # Query Entry Point
    def query(self) -> "SiphonQuery":
        """Create a SiphonQuery instance for this corpus"""
        from .siphon_query import SiphonQuery

        return SiphonQuery(self)


class DatabaseCorpus(SiphonCorpus):
    """Database-backed corpus with lazy SQL query building"""

    def __init__(self, db_connection=get_db_connection):
        """
        Initialize a database-backed corpus.

        Args:
            db_connection_func: contextlib.contextmanager to get a database connection
        """
        self.db_connection = db_connection

    @override
    def __len__(self) -> int:
        """Return the number of items in the corpus."""
        with self.db_connection() as conn, conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM processed_content")
            count = cursor.fetchone()[0]
        return count

    # Collection Management
    @override
    def add(self, content: ProcessedContent) -> None: ...

    @override
    def remove(self, content: ProcessedContent) -> None: ...

    @override
    def remove_by_uri(self, uri: str) -> bool: ...

    # Iteration & Access
    @override
    def __iter__(self):
        with (
            self.db_connection() as conn,
            conn.cursor(cursor_factory=RealDictCursor) as cursor,
        ):
            cursor.execute("SELECT * FROM processed_content")
            while True:
                rows = cursor.fetchmany(1000)  # Batch of 1000
                if not rows:
                    break
                for row in rows:
                    yield ProcessedContent.model_validate_from_cache(row["data"])

    @override
    def __len__(self) -> int: ...

    @override
    def __contains__(self, content: ProcessedContent) -> bool: ...

    # Query Interface (returns new DatabaseCorpus with modified SQL)
    @override
    def filter_by_source_type(self, source_type: SourceType) -> "DatabaseCorpus": ...

    @override
    def filter_by_date_range(self, start_date, end_date) -> "DatabaseCorpus": ...

    @override
    def filter_by_tags(self, tags: list[str]) -> "DatabaseCorpus": ...

    # Database-specific methods
    @override
    def _build_sql_query(self) -> str: ...

    @override
    def _execute_query(self) -> Iterator[ProcessedContent]: ...

    # Metadata & Views
    @override
    def snapshot(self) -> str: ...

    @override
    def get_source_type_counts(self) -> dict[SourceType, int]: ...

    @override
    def is_empty(self) -> bool: ...


class InMemoryCorpus(SiphonCorpus):
    """In-memory corpus for fast operations on materialized data"""

    def __init__(self, source: str, corpus: list[ProcessedContent] = None):
        self.source = source
        self.corpus = corpus if corpus is not None else []

    # Collection Management
    @override
    def add(self, content: ProcessedContent) -> None: ...

    @override
    def remove(self, content: ProcessedContent) -> None: ...

    @override
    def remove_by_uri(self, uri: str) -> bool: ...

    # Iteration & Access
    @override
    def __iter__(self) -> Iterator[ProcessedContent]: ...

    @override
    def __len__(self) -> int: ...

    @override
    def __contains__(self, content: ProcessedContent) -> bool: ...

    # Query Interface (returns new InMemoryCorpus with filtered data)
    @override
    def filter_by_source_type(self, source_type: SourceType) -> "InMemoryCorpus": ...

    @override
    def filter_by_date_range(self, start_date, end_date) -> "InMemoryCorpus": ...

    @override
    def filter_by_tags(self, tags: list[str]) -> "InMemoryCorpus": ...

    # In-memory specific methods
    def text(self) -> str: ...

    def to_dataframe(self): ...

    # Metadata & Views
    @override
    def snapshot(self) -> str: ...

    @override
    def get_source_type_counts(self) -> dict[SourceType, int]: ...

    @override
    def is_empty(self) -> bool: ...


class CorpusFactory:
    """Factory for creating appropriate corpus implementations"""

    # Database-backed creation
    @staticmethod
    def from_library() -> DatabaseCorpus:
        """Create a DatabaseCorpus from the entire library of ProcessedContent."""
        return DatabaseCorpus()

    @staticmethod
    def from_tag(tag: str) -> DatabaseCorpus: ...

    @staticmethod
    def from_date_range(start_date, end_date) -> DatabaseCorpus: ...

    # In-memory creation
    @staticmethod
    def from_directory(
        directory_path: str | Path, pattern: str = "*"
    ) -> InMemoryCorpus: ...

    @staticmethod
    def from_url_list(urls: list[str]) -> InMemoryCorpus: ...

    @staticmethod
    def from_processed_content_list(
        content_list: list[ProcessedContent],
    ) -> InMemoryCorpus: ...

    @staticmethod
    def from_files(file_paths: list[str]) -> InMemoryCorpus: ...


if __name__ == "__main__":
    corpus = CorpusFactory.from_library()
    print(f"Iterated {sum(1 for _ in corpus)} items vs len() = {len(corpus)}")

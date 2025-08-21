"""
ProcessedCorpus - Lightweight wrapper around collections of ProcessedContent objects

Provides convenience functions for managing, constructing, and querying collections
of ProcessedContent. Designed as an ephemeral, in-memory abstraction.
"""

from typing import Literal, Optional
from collections.abc import Iterable
from pathlib import Path
from pydantic import BaseModel, Field

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.types.SourceType import SourceType
from Siphon.main.siphon import siphon
from Siphon.cli.cli_params import CLIParams


class ProcessedCorpus(BaseModel):
    """
    Collection of ProcessedContent objects with rich query and manipulation interface.
    Lightweight wrapper that provides corpus-level operations.
    """

    source: Literal["dir", "urls", "tags"] = Field(
        ..., description="How this corpus was constructed"
    )
    corpus: list[ProcessedContent] = Field(
        default_factory=list, description="Collection of ProcessedContent objects"
    )

    # ============================================================================
    # Constructors - Create corpus from various sources
    # ============================================================================

    @classmethod
    def from_directory(
        cls, directory_path: str | Path, pattern: str = "*"
    ) -> "ProcessedCorpus":
        """
        Create corpus by processing all files in a directory.

        Args:
            directory_path: Path to directory containing files to process
            pattern: File pattern to match (e.g., "*.md", "*.pdf")
        """
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

        return cls(source="dir", corpus=corpus_items)

    @classmethod
    def from_url_list(cls, urls: list[str]) -> "ProcessedCorpus":
        """
        Create corpus by processing a list of URLs.

        Args:
            urls: List of URLs to process (YouTube, GitHub, articles, etc.)
        """
        corpus_items = []

        for url in urls:
            try:
                cli_params = CLIParams(source=url)
                processed_content = siphon(cli_params)
                corpus_items.append(processed_content)
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue

        return cls(source="urls", corpus=corpus_items)

    @classmethod
    def from_tag(cls, tag: str) -> "ProcessedCorpus":
        """
        Create corpus from content tagged with specific tag.

        Args:
            tag: Tag to filter by (e.g., "#strategy", "#research")
        """
        # TODO: Implement tag-based corpus construction
        # This would require adding tag support to ProcessedContent and
        # database queries to find content by tag
        raise NotImplementedError("Tag-based corpus construction not yet implemented")

    @classmethod
    def from_processed_content_list(
        cls, content_list: list[ProcessedContent]
    ) -> "ProcessedCorpus":
        """
        Create corpus from existing ProcessedContent objects.

        Args:
            content_list: List of ProcessedContent objects
        """
        return cls(source="urls", corpus=content_list)  # Generic source type

    # ============================================================================
    # Collection Management - Add/Remove operations
    # ============================================================================

    def add(self, content: ProcessedContent) -> None:
        """Add ProcessedContent to the corpus."""
        if content not in self.corpus:
            self.corpus.append(content)

    def remove(self, content: ProcessedContent) -> None:
        """Remove ProcessedContent from the corpus."""
        if content in self.corpus:
            self.corpus.remove(content)

    def remove_by_uri(self, uri: str) -> bool:
        """
        Remove content by URI string.

        Returns:
            True if content was found and removed, False otherwise
        """
        for content in self.corpus:
            if content.uri.uri == uri:
                self.corpus.remove(content)
                return True
        return False

    # ============================================================================
    # View Operations - Different representations of the corpus
    # ============================================================================

    def snapshot(self) -> str:
        """
        Get high-level overview (titles + descriptions) for quick scanning.
        Perfect for getting the gist of the corpus without full context.
        """
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

    # ============================================================================
    # Query Methods - Search and filter operations
    # ============================================================================

    def search(self, query: str) -> "ProcessedCorpus":
        """
        Simple text search across titles, descriptions, and content.
        Returns new ProcessedCorpus with matching results.
        """
        matching_content = []
        query_lower = query.lower()

        for content in self.corpus:
            # Search in title
            if content.title and query_lower in content.title.lower():
                matching_content.append(content)
                continue

            # Search in description
            if content.description and query_lower in content.description.lower():
                matching_content.append(content)
                continue

            # Search in context (limit to avoid performance issues)
            context_sample = content.context[:1000].lower()
            if query_lower in context_sample:
                matching_content.append(content)

        return ProcessedCorpus.from_processed_content_list(matching_content)

    def similarity_search(self, query: str, k: int = 5) -> "ProcessedCorpus":
        """
        Semantic similarity search using ephemeral vector store.

        Args:
            query: Query text for similarity search
            k: Number of most similar results to return
        """
        # TODO: Implement with in-memory ChromaDB
        # 1. Create ephemeral Chroma collection
        # 2. Add corpus content with embeddings
        # 3. Query for similarity
        # 4. Return top-k results as new ProcessedCorpus
        raise NotImplementedError("Similarity search not yet implemented")

    def filter_by_source_type(self, source_type: SourceType) -> "ProcessedCorpus":
        """Filter corpus by content source type."""
        filtered_content = [
            content for content in self.corpus if content.uri.sourcetype == source_type
        ]
        return ProcessedCorpus.from_processed_content_list(filtered_content)

    def filter_by_date_range(
        self, start_date: Optional[int] = None, end_date: Optional[int] = None
    ) -> "ProcessedCorpus":
        """
        Filter corpus by date range (using content timestamps).

        Args:
            start_date: Unix timestamp for start of range (inclusive)
            end_date: Unix timestamp for end of range (inclusive)
        """
        # TODO: Implement date filtering
        # This requires adding timestamp metadata to ProcessedContent
        raise NotImplementedError("Date range filtering not yet implemented")

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def __len__(self) -> int:
        """Return number of items in corpus."""
        return len(self.corpus)

    def __iter__(self) -> Iterable[ProcessedContent]:
        """Allow iteration over corpus content."""
        return iter(self.corpus)

    def __contains__(self, content: ProcessedContent) -> bool:
        """Check if content is in corpus."""
        return content in self.corpus

    def is_empty(self) -> bool:
        """Check if corpus is empty."""
        return len(self.corpus) == 0

    def get_source_type_counts(self) -> dict[SourceType, int]:
        """Get count of content by source type."""
        counts = {}
        for content in self.corpus:
            source_type = content.uri.sourcetype
            counts[source_type] = counts.get(source_type, 0) + 1
        return counts

    def pretty_print(self) -> None:
        """Display corpus in a beautiful, structured format."""
        print(self.snapshot())

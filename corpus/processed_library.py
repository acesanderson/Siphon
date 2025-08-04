"""
ProcessedLibrary - Persistent, database-backed search interface

Provides library-wide querying across all ProcessedContent stored in the database.
Returns ProcessedCorpus objects for manipulation and analysis.
"""

from typing import Any
from datetime import datetime

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.types.SourceType import SourceType
from Siphon.database.postgres.PGRES_processed_content import (
    get_all_siphon,
    search_cached_content,
    get_cache_stats,
)
from .processed_corpus import ProcessedCorpus


class ProcessedLibrary:
    """
    Database-backed interface for querying across entire Siphon library.

    This class provides persistent storage queries that return ProcessedCorpus
    objects for further manipulation. Acts as the bridge between the database
    layer and the collection abstractions.
    """

    def __init__(self):
        """Initialize library interface."""
        # Could add configuration for different database backends here
        pass

    # ============================================================================
    # Search Operations - Return ProcessedCorpus objects
    # ============================================================================

    def search(self, query: str, limit: int = 50) -> ProcessedCorpus:
        """
        Full-text search across all content in the library.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            ProcessedCorpus containing matching content
        """
        try:
            # Use existing search functionality from PGRES_processed_content
            results = search_cached_content(title_query=query, limit=limit)
            return ProcessedCorpus.from_processed_content_list(results)
        except Exception as e:
            print(f"Search error: {e}")
            return ProcessedCorpus.from_processed_content_list([])

    def similarity_search(self, query: str, k: int = 10) -> ProcessedCorpus:
        """
        Semantic similarity search using persistent vector store.

        Args:
            query: Query for similarity search
            k: Number of similar results to return

        Returns:
            ProcessedCorpus with most similar content
        """
        # TODO: Implement with persistent ChromaDB integration
        # This would use the existing ChromaDB setup but query across
        # all stored content rather than just a single corpus
        raise NotImplementedError("Library-wide similarity search not yet implemented")

    def get_corpus_by_source_type(
        self, source_type: SourceType, limit: int = 100
    ) -> ProcessedCorpus:
        """
        Get all content of a specific source type.

        Args:
            source_type: Type of content to retrieve
            limit: Maximum number of results

        Returns:
            ProcessedCorpus containing content of specified type
        """
        try:
            results = search_cached_content(source_type=source_type.value, limit=limit)
            return ProcessedCorpus.from_processed_content_list(results)
        except Exception as e:
            print(f"Source type query error: {e}")
            return ProcessedCorpus.from_processed_content_list([])

    def get_recent_content(self, days: int = 7, limit: int = 50) -> ProcessedCorpus:
        """
        Get recently processed content.

        Args:
            days: Number of days back to search
            limit: Maximum number of results

        Returns:
            ProcessedCorpus with recent content
        """
        # TODO: Implement date-based queries
        # This requires date filtering in the database layer
        raise NotImplementedError("Recent content queries not yet implemented")

    def get_corpus_by_tag(self, tag: str, limit: int = 100) -> ProcessedCorpus:
        """
        Get all content tagged with a specific tag.

        Args:
            tag: Tag to search for (e.g., "#strategy", "#research")
            limit: Maximum number of results

        Returns:
            ProcessedCorpus containing tagged content
        """
        # TODO: Implement tag-based queries
        # This requires adding tag support to ProcessedContent and database schema
        raise NotImplementedError("Tag-based queries not yet implemented")

    # ============================================================================
    # Corpus Management - Save/Load corpus collections
    # ============================================================================

    def save_corpus(self, corpus: ProcessedCorpus, name: str) -> str:
        """
        Save a ProcessedCorpus as a named collection.

        Args:
            corpus: ProcessedCorpus to save
            name: Name for the saved corpus

        Returns:
            Unique identifier for the saved corpus
        """
        # TODO: Implement corpus persistence
        # This would store:
        # 1. Corpus metadata (name, creation date, source type)
        # 2. List of ProcessedContent URIs in the corpus
        # 3. Allow retrieval by name or ID
        raise NotImplementedError("Corpus persistence not yet implemented")

    def load_corpus(self, name_or_id: str) -> ProcessedCorpus:
        """
        Load a previously saved ProcessedCorpus.

        Args:
            name_or_id: Name or unique identifier of saved corpus

        Returns:
            ProcessedCorpus loaded from storage
        """
        # TODO: Implement corpus loading
        raise NotImplementedError("Corpus loading not yet implemented")

    def list_saved_corpora(self) -> list[dict[str, Any]]:
        """
        List all saved corpus collections.

        Returns:
            List of corpus metadata (name, creation date, size, etc.)
        """
        # TODO: Implement corpus listing
        raise NotImplementedError("Corpus listing not yet implemented")

    # ============================================================================
    # Library Statistics and Management
    # ============================================================================

    def get_all_content(self, limit: int = 1000) -> ProcessedCorpus:
        """
        Get all content in the library (with limit for performance).

        Args:
            limit: Maximum number of items to return

        Returns:
            ProcessedCorpus containing all library content
        """
        try:
            # Use existing function to get all cached content
            all_content = get_all_siphon()

            # Apply limit if needed
            if len(all_content) > limit:
                all_content = all_content[:limit]
                print(f"Warning: Truncated results to {limit} items")

            return ProcessedCorpus.from_processed_content_list(all_content)
        except Exception as e:
            print(f"Error retrieving all content: {e}")
            return ProcessedCorpus.from_processed_content_list([])

    def get_library_stats(self) -> dict[str, Any]:
        """
        Get comprehensive library statistics.

        Returns:
            Dictionary with library statistics and health info
        """
        try:
            # Use existing cache stats function
            cache_stats = get_cache_stats()

            # Add additional library-level stats
            stats = {
                "cache_stats": cache_stats,
                "query_timestamp": datetime.now().isoformat(),
                "library_version": "1.0.0",  # Could be dynamic
            }

            return stats
        except Exception as e:
            return {"error": f"Failed to get library stats: {e}"}

    def health_check(self) -> dict[str, Any]:
        """
        Check library health and connectivity.

        Returns:
            Health status information
        """
        try:
            # Test database connectivity
            stats = self.get_library_stats()

            return {
                "status": "healthy",
                "database_connected": True,
                "total_content": stats.get("cache_stats", {})
                .get("overall", {})
                .get("total_cached", 0),
                "last_checked": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e),
                "last_checked": datetime.now().isoformat(),
            }

    # ============================================================================
    # Advanced Query Operations
    # ============================================================================

    def find_related_content(
        self, content: ProcessedContent, limit: int = 10
    ) -> ProcessedCorpus:
        """
        Find content related to a given ProcessedContent item.

        Args:
            content: ProcessedContent to find relations for
            limit: Maximum number of related items to return

        Returns:
            ProcessedCorpus with related content
        """
        # TODO: Implement relationship detection
        # This could use:
        # 1. Semantic similarity (vector embeddings)
        # 2. Entity extraction and matching
        # 3. Topic modeling
        # 4. Source type patterns
        raise NotImplementedError("Related content detection not yet implemented")

    def get_corpus_by_criteria(self, **filters) -> ProcessedCorpus:
        """
        Flexible query interface supporting multiple filter criteria.

        Args:
            **filters: Various filter criteria:
                - source_type: SourceType
                - title_contains: str
                - min_length: int (minimum content length)
                - max_length: int (maximum content length)
                - has_summary: bool
                - etc.

        Returns:
            ProcessedCorpus matching the criteria
        """
        # TODO: Implement flexible filtering
        # This would build dynamic database queries based on provided filters
        raise NotImplementedError("Flexible criteria queries not yet implemented")

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def __repr__(self) -> str:
        """String representation of the library."""
        try:
            stats = self.get_library_stats()
            total_items = (
                stats.get("cache_stats", {})
                .get("overall", {})
                .get("total_cached", "unknown")
            )
            return f"ProcessedLibrary(total_content={total_items})"
        except:
            return "ProcessedLibrary(status=unknown)"

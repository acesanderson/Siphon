"""
Abstract interface for cache implementations.
This breaks the circular import by defining the contract both implementations follow.
"""

from abc import ABC, abstractmethod
from typing import Optional
from Siphon.data.ProcessedContent import ProcessedContent


class CacheInterface(ABC):
    @abstractmethod
    def get(self, uri_key: str) -> Optional[ProcessedContent]:
        """Retrieve ProcessedContent by URI key"""
        pass

    @abstractmethod
    def store(self, content: ProcessedContent) -> str:
        """Store ProcessedContent, return the uri_key"""
        pass

    @abstractmethod
    def exists(self, uri_key: str) -> bool:
        """Check if content exists without retrieving it"""
        pass


class PostgreSQLCache(CacheInterface):
    """Wrapper around your existing PostgreSQL functions"""

    def get(self, uri_key: str) -> Optional[ProcessedContent]:
        # Import here to avoid circular import
        from Siphon.database.postgres.PGRES_processed_content import (
            get_cached_content_direct,
        )

        return get_cached_content_direct(uri_key)

    def store(self, content: ProcessedContent) -> str:
        from Siphon.database.postgres.PGRES_processed_content import (
            cache_processed_content_direct,
        )

        return cache_processed_content_direct(content)

    def exists(self, uri_key: str) -> bool:
        from Siphon.database.postgres.PGRES_processed_content import cache_exists

        return cache_exists(uri_key)

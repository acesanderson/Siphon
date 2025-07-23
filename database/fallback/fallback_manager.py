"""
Main fallback cache manager - coordinates between PostgreSQL and SQLite
"""

import time
from typing import Optional
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.database.interfaces.cache_interface import PostgreSQLCache
from Siphon.database.sqlite.sqlite_cache import SQLiteCache
from Siphon.database.fallback.sync_queue import SyncQueue
from Siphon.logs.logging_config import get_logger

logger = get_logger(__name__)


class FallbackCacheManager:
    def __init__(self):
        self.postgres_cache = PostgreSQLCache()
        self.sqlite_cache = SQLiteCache()
        self.sync_queue = SyncQueue()
        self._last_postgres_attempt = 0
        self._postgres_retry_interval = 60  # seconds between sync attempts
        self._postgres_available = (
            None  # None=unknown, True=available, False=unavailable
        )

    def get_cached_content(self, uri_key: str) -> Optional[ProcessedContent]:
        """
        Try PostgreSQL first, fall back to SQLite.
        This is your drop-in replacement for get_cached_content()
        """
        # Try PostgreSQL first (if we think it might be available)
        if self._postgres_available is not False:
            try:
                content = self.postgres_cache.get(uri_key)
                if content:
                    # PostgreSQL worked! Mark it as available and ensure SQLite backup
                    self._postgres_available = True
                    try:
                        self.sqlite_cache.store(content)
                    except Exception as e:
                        logger.warning(f"Failed to backup to SQLite: {e}")

                    # Since PostgreSQL is working, try to clear sync backlog
                    self._try_sync_backlog()
                    return content
            except Exception as e:
                logger.debug(f"PostgreSQL unavailable: {e}")
                self._postgres_available = False

        # Fall back to SQLite
        content = self.sqlite_cache.get(uri_key)
        if content:
            logger.info(f"SQLite cache hit for {uri_key}")

        return content

    def cache_processed_content(self, content: ProcessedContent) -> str:
        """
        Always cache to SQLite, try PostgreSQL, queue if it fails.
        This is your drop-in replacement for cache_processed_content()
        """
        uri_key = content.uri.uri

        # Always store in SQLite first (this should never fail)
        try:
            self.sqlite_cache.store(content)
            logger.debug(f"Cached to SQLite: {uri_key}")
        except Exception as e:
            logger.error(f"SQLite cache failed (this is bad!): {e}")
            # Still try PostgreSQL even if SQLite failed

        # Try PostgreSQL if we think it might be available
        if self._postgres_available is not False:
            try:
                result = self.postgres_cache.store(content)
                logger.debug(f"Cached to PostgreSQL: {uri_key}")
                self._postgres_available = True

                # Since PostgreSQL worked, try to clear any backlog
                self._try_sync_backlog()
                return result

            except Exception as e:
                logger.info(
                    f"PostgreSQL cache failed, queuing for sync: {uri_key} - {e}"
                )
                self._postgres_available = False

                # Queue for later sync
                self.sync_queue.add_pending_sync(content)
        else:
            # We know PostgreSQL is down, so just queue it
            logger.debug(f"PostgreSQL known to be down, queuing: {uri_key}")
            self.sync_queue.add_pending_sync(content)

        return uri_key

    def _try_sync_backlog(self):
        """Opportunistically sync queued items when PostgreSQL is working"""
        current_time = time.time()

        # Don't spam sync attempts
        if current_time - self._last_postgres_attempt < self._postgres_retry_interval:
            return

        self._last_postgres_attempt = current_time

        if self.sync_queue.queue:
            result = self.sync_queue.process_sync_batch()
            if result["synced"] > 0:
                logger.info(
                    f"Synced {result['synced']} items from backlog to PostgreSQL"
                )

            # If we had failures, PostgreSQL might be down again
            if result["failed"] > 0:
                self._postgres_available = False

    def force_sync_backlog(self, batch_size: int = 50) -> dict:
        """
        Manually trigger a sync attempt (useful for debugging or manual intervention)
        Returns sync statistics
        """
        logger.info("Manual sync backlog triggered")
        result = self.sync_queue.process_sync_batch(batch_size=batch_size)

        # Update PostgreSQL availability based on results
        if result["synced"] > 0:
            self._postgres_available = True
        elif result["failed"] > 0 and result["synced"] == 0:
            self._postgres_available = False

        return result

    def get_fallback_stats(self) -> dict:
        """Get comprehensive statistics about the fallback cache system"""
        try:
            sqlite_stats = self.sqlite_cache.get_stats()
        except Exception as e:
            sqlite_stats = {"error": str(e)}

        queue_stats = self.sync_queue.get_queue_stats()

        return {
            "postgres_available": self._postgres_available,
            "last_postgres_attempt": self._last_postgres_attempt,
            "sqlite_cache": sqlite_stats,
            "sync_queue": queue_stats,
            "next_sync_items": self.sync_queue.peek_next_items(3),
        }

    def cache_exists(self, uri_key: str) -> bool:
        """Check if content exists in either cache"""
        # Try PostgreSQL first if available
        if self._postgres_available is not False:
            try:
                if self.postgres_cache.exists(uri_key):
                    self._postgres_available = True
                    return True
            except Exception:
                self._postgres_available = False

        # Check SQLite
        return self.sqlite_cache.exists(uri_key)

    def clear_all_caches(self) -> dict:
        """Clear both caches and sync queue. Use with caution!"""
        results = {}

        try:
            results["sqlite_cleared"] = self.sqlite_cache.clear_cache()
        except Exception as e:
            results["sqlite_error"] = str(e)

        try:
            results["queue_cleared"] = self.sync_queue.clear_queue()
        except Exception as e:
            results["queue_error"] = str(e)

        logger.warning(f"Cleared all fallback caches: {results}")
        return results

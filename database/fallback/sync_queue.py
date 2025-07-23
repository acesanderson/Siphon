"""
Queue management for syncing SQLite cache to PostgreSQL when connection is restored
"""

import time
from collections import deque
from threading import Lock
from typing import Any
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.logs.logging_config import get_logger

logger = get_logger(__name__)


class SyncQueue:
    def __init__(self, max_queue_size: int = 1000):
        self.queue = deque()
        self.lock = Lock()  # Thread safety for concurrent access
        self.max_queue_size = max_queue_size
        self._dropped_items = 0  # Track if we had to drop items due to size

    def add_pending_sync(self, content: ProcessedContent) -> bool:
        """
        Add content that needs to sync to PostgreSQL.
        Returns True if added, False if queue is full and item was dropped.
        """
        with self.lock:
            # Check if we're at capacity
            if len(self.queue) >= self.max_queue_size:
                # Drop the oldest item to make room
                dropped = self.queue.popleft()
                self._dropped_items += 1
                logger.warning(
                    f"Sync queue full, dropped oldest item: {dropped['uri_key']} "
                    f"(total dropped: {self._dropped_items})"
                )

            # Add the new item
            sync_item = {
                "operation": "store",
                "content": content,
                "timestamp": time.time(),
                "uri_key": content.uri.uri,
                "retry_count": 0,
            }

            self.queue.append(sync_item)
            logger.debug(
                f"Added to sync queue: {content.uri.uri} (queue size: {len(self.queue)})"
            )
            return True

    def process_sync_batch(
        self, batch_size: int = 10, max_retries: int = 3
    ) -> dict[str, int]:
        """
        Process a batch of pending syncs.
        Returns dict with 'synced', 'failed', 'requeued' counts.
        """
        if not self.queue:
            return {"synced": 0, "failed": 0, "requeued": 0}

        synced = 0
        failed = 0
        requeued = 0

        # Process up to batch_size items
        for _ in range(min(batch_size, len(self.queue))):
            if not self.queue:
                break

            with self.lock:
                pending_item = self.queue.popleft()

            try:
                # Import here to avoid circular imports
                from Siphon.database.interfaces.cache_interface import PostgreSQLCache

                postgres_cache = PostgreSQLCache()

                # Try to sync to PostgreSQL
                postgres_cache.store(pending_item["content"])
                synced += 1
                logger.debug(f"Synced to PostgreSQL: {pending_item['uri_key']}")

            except Exception as e:
                pending_item["retry_count"] += 1

                if pending_item["retry_count"] <= max_retries:
                    # Put it back at the front for retry
                    with self.lock:
                        self.queue.appendleft(pending_item)
                    requeued += 1
                    logger.debug(
                        f"Sync failed, requeued (attempt {pending_item['retry_count']}): "
                        f"{pending_item['uri_key']} - {e}"
                    )
                else:
                    # Give up after max retries
                    failed += 1
                    logger.error(
                        f"Sync failed permanently after {max_retries} attempts: "
                        f"{pending_item['uri_key']} - {e}"
                    )

                # If PostgreSQL is still down, don't try more items
                if "Connection" in str(e) or "connection" in str(e).lower():
                    logger.debug("PostgreSQL appears to be down, stopping batch sync")
                    break

        result = {"synced": synced, "failed": failed, "requeued": requeued}

        if synced > 0 or failed > 0:
            logger.info(f"Sync batch completed: {result}")

        return result

    def get_queue_stats(self) -> dict[str, Any]:
        """Get statistics about the current sync queue"""
        with self.lock:
            if not self.queue:
                return {
                    "queue_size": 0,
                    "oldest_item_age_seconds": 0,
                    "newest_item_age_seconds": 0,
                    "dropped_items_total": self._dropped_items,
                }

            current_time = time.time()
            oldest_timestamp = min(item["timestamp"] for item in self.queue)
            newest_timestamp = max(item["timestamp"] for item in self.queue)

            return {
                "queue_size": len(self.queue),
                "oldest_item_age_seconds": current_time - oldest_timestamp,
                "newest_item_age_seconds": current_time - newest_timestamp,
                "dropped_items_total": self._dropped_items,
                "max_queue_size": self.max_queue_size,
            }

    def clear_queue(self) -> int:
        """Clear all pending sync items. Returns number of items cleared."""
        with self.lock:
            cleared_count = len(self.queue)
            self.queue.clear()
            logger.warning(
                f"Cleared sync queue. Removed {cleared_count} pending items."
            )
            return cleared_count

    def peek_next_items(self, count: int = 5) -> list[dict[str, Any]]:
        """Peek at the next few items in the queue without removing them"""
        with self.lock:
            items = []
            for i, item in enumerate(self.queue):
                if i >= count:
                    break
                items.append(
                    {
                        "uri_key": item["uri_key"],
                        "timestamp": item["timestamp"],
                        "retry_count": item["retry_count"],
                        "age_seconds": time.time() - item["timestamp"],
                    }
                )
            return items

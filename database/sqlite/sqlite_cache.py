"""
SQLite cache implementation - completely independent of PostgreSQL code
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.database.interfaces.cache_interface import CacheInterface
from Siphon.logs.logging_config import get_logger

logger = get_logger(__name__)


class SQLiteCache(CacheInterface):
    def __init__(self, db_path: str = "~/.siphon/fallback_cache.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Create the SQLite table mirroring PostgreSQL schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uri_key TEXT UNIQUE NOT NULL,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sqlite_uri_key 
                ON processed_content(uri_key)
            """)
            logger.debug(f"SQLite cache initialized at {self.db_path}")

    def get(self, uri_key: str) -> Optional[ProcessedContent]:
        """Retrieve ProcessedContent by URI key"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Access columns by name
                cursor = conn.execute(
                    "SELECT data FROM processed_content WHERE uri_key = ?", (uri_key,)
                )
                row = cursor.fetchone()

                if not row:
                    logger.debug(f"SQLite cache miss for URI: {uri_key}")
                    return None

                try:
                    # Use your existing factory-based reconstruction
                    processed_content = ProcessedContent.model_validate_from_cache(
                        json.loads(row["data"])
                    )
                    logger.debug(f"SQLite cache hit for URI: {uri_key}")
                    return processed_content
                except Exception as e:
                    logger.error(
                        f"Failed to deserialize SQLite content for {uri_key}: {e}"
                    )
                    return None
        except Exception as e:
            logger.error(f"SQLite database error for {uri_key}: {e}")
            return None

    def store(self, content: ProcessedContent) -> str:
        """Store ProcessedContent in SQLite"""
        uri_key = content.uri.uri

        try:
            data_json = json.dumps(content.model_dump_for_cache())

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO processed_content 
                    (uri_key, data, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (uri_key, data_json),
                )

                logger.debug(f"Stored in SQLite cache: {uri_key}")
                return uri_key
        except Exception as e:
            logger.error(f"Failed to store in SQLite cache {uri_key}: {e}")
            raise

    def exists(self, uri_key: str) -> bool:
        """Check if content exists without retrieving it"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM processed_content WHERE uri_key = ?", (uri_key,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"SQLite exists check failed for {uri_key}: {e}")
            return False

    def get_stats(self) -> dict:
        """Get basic statistics about the SQLite cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_cached,
                        MIN(created_at) as oldest_cached,
                        MAX(updated_at) as most_recent_update
                    FROM processed_content
                """)
                stats = cursor.fetchone()

                # Get file size
                file_size = self.db_path.stat().st_size if self.db_path.exists() else 0

                return {
                    "total_cached": stats[0] if stats else 0,
                    "oldest_cached": stats[1] if stats else None,
                    "most_recent_update": stats[2] if stats else None,
                    "file_size_bytes": file_size,
                    "db_path": str(self.db_path),
                }
        except Exception as e:
            logger.error(f"Failed to get SQLite stats: {e}")
            return {"error": str(e)}

    def clear_cache(self) -> int:
        """Clear all cached data. Returns number of deleted records."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM processed_content")
                deleted_count = cursor.rowcount
                logger.warning(
                    f"Cleared SQLite cache. Deleted {deleted_count} records."
                )
                return deleted_count
        except Exception as e:
            logger.error(f"Failed to clear SQLite cache: {e}")
            return 0

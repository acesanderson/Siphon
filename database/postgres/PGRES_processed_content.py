"""
CRUD functions for Siphon project. Adapted from Kramer.database.

We will use this database as a cache for siphon data, keyed to uri.uri.
Uses factory-based serialization for robust object reconstruction.

Now includes fallback cache system for when PostgreSQL is unavailable.
"""

from typing import Optional, Any
from psycopg2.extras import RealDictCursor, Json

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.database.postgres.PGRES_connection import get_db_connection
from Siphon.logs.logging_config import get_logger
from rich.console import Console

console = Console()
logger = get_logger(__name__)


def create_table():
    """Create the processed_content table with simple JSONB storage."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processed_content (
                    id SERIAL PRIMARY KEY,
                    uri_key TEXT UNIQUE NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)

            # Index for cache lookups (most important) - B-tree for exact matches
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_content_uri_key 
                ON processed_content(uri_key);
            """)

            # GIN index for JSONB queries (this is correct usage)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_content_jsonb 
                ON processed_content USING gin(data);
            """)

            # B-tree index for timestamp queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_content_updated_at 
                ON processed_content(updated_at DESC);
            """)

        conn.commit()
        logger.info("ProcessedContent cache table created successfully")


def ensure_table_exists():
    """Ensure the processed_content table exists, create if not."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'processed_content'
                );
            """)

            table_exists = cur.fetchone()[0]

            if not table_exists:
                logger.info("processed_content table not found, creating...")
                create_table()
                return True
            return False


# =============================================================================
# DIRECT POSTGRESQL FUNCTIONS (used by fallback system)
# =============================================================================


def get_cached_content_direct(uri_key: str) -> Optional[ProcessedContent]:
    """
    Direct PostgreSQL access - used by fallback system.
    Retrieve ProcessedContent from cache by URI key.
    """
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT data FROM processed_content 
                WHERE uri_key = %s
            """,
                (uri_key,),
            )

            row = cur.fetchone()
            if not row:
                logger.debug(f"PostgreSQL cache miss for URI: {uri_key}")
                return None

            try:
                # Deserialize using factory-based reconstruction
                processed_content = ProcessedContent.model_validate_from_cache(
                    row["data"]
                )
                logger.debug(f"PostgreSQL cache hit for URI: {uri_key}")
                return processed_content
            except Exception as e:
                logger.error(
                    f"Failed to deserialize PostgreSQL cached content for {uri_key}: {e}"
                )
                return None


def cache_processed_content_direct(processed_content: ProcessedContent) -> str:
    """
    Direct PostgreSQL access - used by fallback system.
    Cache a ProcessedContent object using factory-friendly serialization.
    """
    ensure_table_exists()

    uri_key = processed_content.uri.uri
    data_json = processed_content.model_dump_for_cache()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Use ON CONFLICT to handle cache updates
            cur.execute(
                """
                INSERT INTO processed_content (uri_key, data, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (uri_key) 
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    updated_at = NOW()
                RETURNING uri_key;
            """,
                (uri_key, Json(data_json)),
            )

            result = cur.fetchone()
            conn.commit()

            logger.info(f"Cached content to PostgreSQL with URI: {uri_key}")
            return result[0] if result else uri_key


# =============================================================================
# INITIALIZE FALLBACK SYSTEM
# =============================================================================

# Try to initialize the fallback cache manager
try:
    from Siphon.database.fallback.fallback_manager import FallbackCacheManager

    _fallback_manager = FallbackCacheManager()
    _fallback_enabled = True
    logger.info("Fallback cache manager initialized successfully")
except Exception as e:
    logger.warning(f"Fallback cache manager failed to initialize: {e}")
    logger.warning("Falling back to direct PostgreSQL access only")
    _fallback_manager = None
    _fallback_enabled = False


# =============================================================================
# PUBLIC INTERFACE FUNCTIONS (with fallback support)
# =============================================================================


def get_cached_content(uri_key: str) -> Optional[ProcessedContent]:
    """
    Public interface with fallback support.
    Retrieve ProcessedContent from cache by URI key.
    Auto-creates table if it doesn't exist.
    """
    if _fallback_enabled and _fallback_manager:
        return _fallback_manager.get_cached_content(uri_key)
    else:
        # Fallback to direct PostgreSQL access
        logger.debug("Using direct PostgreSQL access (fallback system unavailable)")
        return get_cached_content_direct(uri_key)


def cache_processed_content(processed_content: ProcessedContent) -> str:
    """
    Public interface with fallback support.
    Cache a ProcessedContent object.
    Auto-creates table if it doesn't exist.
    """
    if _fallback_enabled and _fallback_manager:
        return _fallback_manager.cache_processed_content(processed_content)
    else:
        # Fallback to direct PostgreSQL access
        logger.debug("Using direct PostgreSQL access (fallback system unavailable)")
        return cache_processed_content_direct(processed_content)


def cache_exists(uri_key: str) -> bool:
    """Check if content exists in cache without retrieving it."""
    if _fallback_enabled and _fallback_manager:
        return _fallback_manager.cache_exists(uri_key)
    else:
        # Direct PostgreSQL check
        try:
            ensure_table_exists()
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1 FROM processed_content 
                        WHERE uri_key = %s
                    """,
                        (uri_key,),
                    )
                    return cur.fetchone() is not None
        except Exception as e:
            logger.error(f"Failed to check cache existence for {uri_key}: {e}")
            return False


# =============================================================================
# FALLBACK MANAGEMENT FUNCTIONS
# =============================================================================


def get_fallback_stats() -> dict:
    """Get statistics about the fallback cache system"""
    if _fallback_enabled and _fallback_manager:
        return _fallback_manager.get_fallback_stats()
    else:
        return {
            "fallback_enabled": False,
            "reason": "Fallback system not initialized",
            "postgres_only": True,
        }


def force_sync_backlog(batch_size: int = 50) -> dict:
    """Manually trigger a sync of the backlog queue"""
    if _fallback_enabled and _fallback_manager:
        return _fallback_manager.force_sync_backlog(batch_size)
    else:
        return {"error": "Fallback system not available", "fallback_enabled": False}


def clear_all_caches() -> dict:
    """Clear both fallback caches and PostgreSQL cache. Use with caution!"""
    results = {}

    # Clear fallback caches if available
    if _fallback_enabled and _fallback_manager:
        fallback_results = _fallback_manager.clear_all_caches()
        results.update(fallback_results)

    # Clear PostgreSQL cache
    try:
        postgres_cleared = clear_table()
        results["postgres_cleared"] = postgres_cleared
    except Exception as e:
        results["postgres_error"] = str(e)

    logger.warning(f"Cleared all caches: {results}")
    return results


# =============================================================================
# LEGACY FUNCTIONS (maintained for backward compatibility)
# =============================================================================


def insert_siphon(siphon: ProcessedContent) -> str:
    """
    Legacy function - maintained for backward compatibility.
    Use cache_processed_content() instead.
    """
    logger.warning(
        "insert_siphon() is deprecated. Use cache_processed_content() instead."
    )
    return cache_processed_content_direct(siphon)


def get_siphon_by_uri(uri_key: str) -> Optional[ProcessedContent]:
    """
    Legacy function - maintained for backward compatibility.
    Use get_cached_content() instead.
    """
    logger.warning(
        "get_siphon_by_uri() is deprecated. Use get_cached_content() instead."
    )
    return get_cached_content(uri_key)


def get_siphon_by_id(id: str) -> Optional[ProcessedContent]:
    """Retrieve ProcessedContent by database ID (PostgreSQL only)."""
    try:
        record_id = int(id)
    except ValueError:
        logger.error(f"Invalid ID format: {id}")
        return None

    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT data FROM processed_content 
                WHERE id = %s
            """,
                (record_id,),
            )

            row = cur.fetchone()
            if not row:
                return None

            try:
                return ProcessedContent.model_validate_from_cache(row["data"])
            except Exception as e:
                logger.error(f"Failed to deserialize content with ID {record_id}: {e}")
                return None


def get_all_siphon() -> list[ProcessedContent]:
    """
    Get all cached ProcessedContent objects (PostgreSQL only).
    Returns most recently updated first.
    """
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data FROM processed_content 
                ORDER BY updated_at DESC 
                LIMIT 100
            """)

            rows = cur.fetchall()
            results = []

            for row in rows:
                try:
                    processed_content = ProcessedContent.model_validate_from_cache(
                        row["data"]
                    )
                    results.append(processed_content)
                except Exception as e:
                    logger.warning(f"Skipping invalid cached content: {e}")
                    continue

            return results


def search_cached_content(
    source_type: Optional[str] = None,
    title_query: Optional[str] = None,
    limit: int = 50,
) -> list[ProcessedContent]:
    """
    Basic search functionality using JSONB queries (PostgreSQL only).

    Args:
        source_type: Filter by source type (e.g., 'YouTube', 'GitHub')
        title_query: Search in titles using full-text search
        limit: Maximum results to return
    """
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            where_conditions = []
            params = []

            if source_type:
                where_conditions.append("data->>'sourcetype' = %s")
                params.append(source_type)

            if title_query:
                where_conditions.append("""
                    to_tsvector('english', COALESCE(data->'synthetic_data'->>'title', ''))
                    @@ plainto_tsquery('english', %s)
                """)
                params.append(title_query)

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            cur.execute(
                f"""
                SELECT data FROM processed_content
                {where_clause}
                ORDER BY updated_at DESC
                LIMIT %s
            """,
                params + [limit],
            )

            rows = cur.fetchall()
            results = []

            for row in rows:
                try:
                    processed_content = ProcessedContent.model_validate_from_cache(
                        row["data"]
                    )
                    results.append(processed_content)
                except Exception as e:
                    logger.warning(f"Skipping invalid search result: {e}")
                    continue

            return results


def delete_cached_content(uri_key: str) -> bool:
    """Delete cached content by URI key. Returns True if deleted (PostgreSQL only)."""
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM processed_content 
                WHERE uri_key = %s
            """,
                (uri_key,),
            )

            deleted = cur.rowcount > 0
            conn.commit()

            if deleted:
                logger.info(f"Deleted cached content from PostgreSQL: {uri_key}")

            return deleted


def get_cache_stats() -> dict[str, Any]:
    """Get basic statistics about the PostgreSQL cache."""
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_cached,
                    COUNT(DISTINCT data->>'sourcetype') as unique_source_types,
                    MIN(created_at) as oldest_cached,
                    MAX(updated_at) as most_recent_update,
                    pg_size_pretty(pg_total_relation_size('processed_content')) as table_size
            """)
            overall_stats = cur.fetchone()

            # Source type breakdown
            cur.execute("""
                SELECT 
                    data->>'sourcetype' as source_type,
                    COUNT(*) as count
                FROM processed_content 
                GROUP BY data->>'sourcetype'
                ORDER BY count DESC
            """)
            source_type_stats = cur.fetchall()

            return {
                "overall": dict(overall_stats) if overall_stats else {},
                "by_source_type": [dict(row) for row in source_type_stats],
            }


def clear_table():
    """Clear all cached data from PostgreSQL. Use with caution!"""
    ensure_table_exists()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM processed_content")
            deleted_count = cur.rowcount
            conn.commit()

            logger.warning(
                f"Cleared all PostgreSQL cached content. Deleted {deleted_count} records."
            )
            return deleted_count


def delete_table():
    """Delete the entire PostgreSQL table. Use only for testing!"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS processed_content CASCADE")
            conn.commit()

            logger.warning("Deleted processed_content table entirely.")


# =============================================================================
# DEBUG AND UTILITY FUNCTIONS
# =============================================================================


def debug_cache_status() -> dict:
    """Debug function to check the status of all cache systems"""
    status = {
        "fallback_enabled": _fallback_enabled,
        "fallback_manager_available": _fallback_manager is not None,
        "postgres_connection": None,
        "fallback_stats": None,
    }

    # Test PostgreSQL connection
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                status["postgres_connection"] = "available"
    except Exception as e:
        status["postgres_connection"] = f"failed: {e}"

    # Get fallback stats if available
    if _fallback_enabled and _fallback_manager:
        try:
            status["fallback_stats"] = _fallback_manager.get_fallback_stats()
        except Exception as e:
            status["fallback_stats"] = f"error: {e}"

    return status


def is_fallback_enabled() -> bool:
    """Check if the fallback system is enabled and available"""
    return _fallback_enabled and _fallback_manager is not None

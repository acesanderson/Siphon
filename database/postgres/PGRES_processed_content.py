"""
CRUD functions for Siphon project. Adapted from Kramer.database.

We will use this database as a cache for siphon data, keyed to uri.uri.
Uses factory-based serialization for robust object reconstruction.
"""

from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from Siphon.database.postgres.PGRES_connection import get_db_connection
from Siphon.logs.logging_config import get_logger
from rich.console import Console

console = Console()
logger = get_logger(__name__)


"""
Fixed create_table function with proper index types
"""

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

def insert_siphon(siphon: ProcessedContent) -> str:
    """
    Cache a ProcessedContent object using factory-friendly serialization.
    Returns the URI key used for caching.
    """
    uri_key = siphon.uri.uri
    data_json = siphon.model_dump_for_cache()
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Use ON CONFLICT to handle cache updates
            cur.execute("""
                INSERT INTO processed_content (uri_key, data, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (uri_key) 
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    updated_at = NOW()
                RETURNING uri_key;
            """, (uri_key, Json(data_json)))
            
            result = cur.fetchone()
            conn.commit()
            
            logger.info(f"Cached content with URI: {uri_key}")
            return result[0] if result else uri_key


def get_siphon_by_id(id: str) -> Optional[ProcessedContent]:
    """Retrieve ProcessedContent by database ID."""
    try:
        record_id = int(id)
    except ValueError:
        logger.error(f"Invalid ID format: {id}")
        return None
        
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data FROM processed_content 
                WHERE id = %s
            """, (record_id,))
            
            row = cur.fetchone()
            if not row:
                return None
                
            try:
                return ProcessedContent.model_validate_from_cache(row['data'])
            except Exception as e:
                logger.error(f"Failed to deserialize content with ID {record_id}: {e}")
                return None


def get_siphon_by_uri(uri_key: str) -> Optional[ProcessedContent]:
    """
    Retrieve ProcessedContent from cache by URI key.
    Returns None if not found.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data FROM processed_content 
                WHERE uri_key = %s
            """, (uri_key,))
            
            row = cur.fetchone()
            if not row:
                logger.debug(f"Cache miss for URI: {uri_key}")
                return None
                
            try:
                # Deserialize using factory-based reconstruction
                processed_content = ProcessedContent.model_validate_from_cache(row['data'])
                logger.debug(f"Cache hit for URI: {uri_key}")
                return processed_content
            except Exception as e:
                logger.error(f"Failed to deserialize cached content for {uri_key}: {e}")
                return None


def get_all_siphon() -> List[ProcessedContent]:
    """
    Get all cached ProcessedContent objects.
    Returns most recently updated first.
    """
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
                    processed_content = ProcessedContent.model_validate_from_cache(row['data'])
                    results.append(processed_content)
                except Exception as e:
                    logger.warning(f"Skipping invalid cached content: {e}")
                    continue
                    
            return results


def search_cached_content(
    source_type: Optional[str] = None,
    title_query: Optional[str] = None,
    limit: int = 50
) -> List[ProcessedContent]:
    """
    Basic search functionality using JSONB queries.
    
    Args:
        source_type: Filter by source type (e.g., 'YouTube', 'GitHub')
        title_query: Search in titles using full-text search
        limit: Maximum results to return
    """
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
            
            cur.execute(f"""
                SELECT data FROM processed_content
                {where_clause}
                ORDER BY updated_at DESC
                LIMIT %s
            """, params + [limit])
            
            rows = cur.fetchall()
            results = []
            
            for row in rows:
                try:
                    processed_content = ProcessedContent.model_validate_from_cache(row['data'])
                    results.append(processed_content)
                except Exception as e:
                    logger.warning(f"Skipping invalid search result: {e}")
                    continue
                    
            return results


def cache_exists(uri_key: str) -> bool:
    """Check if content exists in cache without retrieving it."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM processed_content 
                WHERE uri_key = %s
            """, (uri_key,))
            
            return cur.fetchone() is not None


def delete_cached_content(uri_key: str) -> bool:
    """Delete cached content by URI key. Returns True if deleted."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM processed_content 
                WHERE uri_key = %s
            """, (uri_key,))
            
            deleted = cur.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted cached content: {uri_key}")
            
            return deleted


def get_cache_stats() -> Dict[str, Any]:
    """Get basic statistics about the cache."""
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
                "by_source_type": [dict(row) for row in source_type_stats]
            }


def clear_table():
    """Clear all cached data. Use with caution!"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM processed_content")
            deleted_count = cur.rowcount
            conn.commit()
            
            logger.warning(f"Cleared all cached content. Deleted {deleted_count} records.")
            return deleted_count


def delete_table():
    """Delete the entire table. Use only for testing!"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS processed_content CASCADE")
            conn.commit()
            
            logger.warning("Deleted processed_content table entirely.")


# Convenience aliases for cleaner naming
"""
Add this function and modify get_cached_content to auto-initialize the table
"""
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


def get_cached_content(uri_key: str) -> Optional[ProcessedContent]:
    """
    Retrieve ProcessedContent from cache by URI key.
    Auto-creates table if it doesn't exist.
    """
    # Ensure table exists before querying
    ensure_table_exists()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data FROM processed_content 
                WHERE uri_key = %s
            """, (uri_key,))
            
            row = cur.fetchone()
            if not row:
                logger.debug(f"Cache miss for URI: {uri_key}")
                return None
                
            try:
                # Deserialize using factory-based reconstruction
                processed_content = ProcessedContent.model_validate_from_cache(row['data'])
                logger.debug(f"Cache hit for URI: {uri_key}")
                return processed_content
            except Exception as e:
                logger.error(f"Failed to deserialize cached content for {uri_key}: {e}")
                return None


def cache_processed_content(processed_content: ProcessedContent) -> str:
    """
    Cache a ProcessedContent object.
    Auto-creates table if it doesn't exist.
    """
    # Ensure table exists before inserting
    ensure_table_exists()
    
    return insert_siphon(processed_content)


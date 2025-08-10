#!/usr/bin/env python3
"""
PostgreSQL cache snapshot utility - standalone CLI for library overview
"""

import argparse
from Siphon.database.postgres.PGRES_connection import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


def get_total_count():
    """Total cached items"""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM processed_content")
        return cur.fetchone()[0]


def get_source_type_bars():
    """Source type distribution with horizontal bars"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
           SELECT data->>'sourcetype' as source_type, COUNT(*) as count 
           FROM processed_content 
           GROUP BY data->>'sourcetype' 
           ORDER BY count DESC
       """)
        results = cur.fetchall()

        if not results:
            return "No data found"

        max_count = max(r["count"] for r in results)
        output = []

        for row in results:
            bar_length = int((row["count"] / max_count) * 40)
            bar = "█" * bar_length
            output.append(f"{row['source_type']:<12} {bar} {row['count']}")

        return "\n".join(output)


def get_recent_additions(hours=24):
    """Recent additions in last N hours"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cutoff = datetime.now() - timedelta(hours=hours)
        cur.execute(
            """
           SELECT data->>'sourcetype' as source_type, 
                  data->'synthetic_data'->>'title' as title,
                  created_at
           FROM processed_content 
           WHERE created_at > %s 
           ORDER BY created_at DESC 
           LIMIT 10
       """,
            (cutoff,),
        )

        results = cur.fetchall()
        if not results:
            return f"No additions in last {hours}h"

        output = [f"Last {hours}h ({len(results)} items):"]
        for row in results:
            title = (row["title"] or "Untitled")[:50]
            time_str = row["created_at"].strftime("%m/%d %H:%M")
            output.append(f"  {time_str} {row['source_type']:<8} {title}")

        return "\n".join(output)


def get_latest_items():
    """Three most recently added items"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT data->>'sourcetype' as source_type,
                   COALESCE(data->'synthetic_data'->>'title', 'Untitled') as title,
                   created_at
            FROM processed_content 
            ORDER BY created_at DESC 
            LIMIT 3
        """)

        results = cur.fetchall()
        output = ["Latest:"]
        for row in results:
            title = row["title"][:40]
            date_str = row["created_at"].strftime("%m/%d %H:%M")
            output.append(f"  {date_str} {row['source_type']:<8} {title}")

        return "\n".join(output)


def get_size_extremes():
    """Largest and smallest content by character count"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get largest
        cur.execute("""
            SELECT data->>'sourcetype' as source_type,
                   COALESCE(data->'synthetic_data'->>'title', 'Untitled') as title,
                   LENGTH(data->'context_data'->>'context') as size
            FROM processed_content 
            WHERE data->'context_data'->>'context' IS NOT NULL
            ORDER BY size DESC LIMIT 3
        """)
        largest = cur.fetchall()

        # Get smallest
        cur.execute("""
            SELECT data->>'sourcetype' as source_type,
                   COALESCE(data->'synthetic_data'->>'title', 'Untitled') as title,
                   LENGTH(data->'context_data'->>'context') as size
            FROM processed_content 
            WHERE data->'context_data'->>'context' IS NOT NULL
            ORDER BY size ASC LIMIT 3
        """)
        smallest = cur.fetchall()

        output = ["Largest:"]
        for row in largest:
            title = row["title"][:40]
            size = row["size"] or 0
            output.append(f"  {size:>6} chars {row['source_type']:<8} {title}")

        output.append("\nSmallest:")
        for row in smallest:
            title = row["title"][:40]
            size = row["size"] or 0
            output.append(f"  {size:>6} chars {row['source_type']:<8} {title}")

        return "\n".join(output)


def search_by_source_type(source_type):
    """Show items for specific source type"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
           SELECT data->'synthetic_data'->>'title' as title,
                  data->'llm_context'->>'url' as url,
                  created_at
           FROM processed_content 
           WHERE data->>'sourcetype' = %s 
           ORDER BY created_at DESC 
           LIMIT 20
       """,
            (source_type,),
        )

        results = cur.fetchall()
        if not results:
            return f"No {source_type} items found"

        output = [f"{source_type} items ({len(results)}):"]
        for row in results:
            title = (row["title"] or "Untitled")[:50]
            date_str = row["created_at"].strftime("%m/%d")
            output.append(f"  {date_str} {title}")

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL cache snapshot")
    parser.add_argument("--source-type", help="Show items for specific source type")
    parser.add_argument(
        "--recent", type=int, default=24, help="Recent hours (default: 24)"
    )

    args = parser.parse_args()

    if args.source_type:
        print(search_by_source_type(args.source_type))
        return

    # Default overview
    print("=== SIPHON LIBRARY SNAPSHOT ===\n")
    print(f"Total items: {get_total_count()}\n")
    print("Source types:")
    print(get_source_type_bars())
    print(f"\n{get_recent_additions(args.recent)}")
    print(f"\n{get_latest_items()}")
    print(f"\n{get_size_extremes()}")


if __name__ == "__main__":
    main()

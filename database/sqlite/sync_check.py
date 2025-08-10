#!/usr/bin/env python3
"""
Simple script to check if SQLite fallback content has been synced to PostgreSQL.
Directly queries both databases without depending on fallback system being active.
"""

import sqlite3
import sys
from pathlib import Path


def get_sqlite_stats():
    """Get stats from SQLite fallback database."""
    sqlite_path = Path("~/.siphon/fallback_cache.db").expanduser()

    if not sqlite_path.exists():
        return None, "SQLite database does not exist"

    try:
        with sqlite3.connect(sqlite_path) as conn:
            cursor = conn.cursor()

            # Get total count
            cursor.execute("SELECT COUNT(*) FROM processed_content")
            total_count = cursor.fetchone()[0]

            # Get oldest and newest
            cursor.execute("""
                SELECT 
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM processed_content
            """)
            oldest, newest = cursor.fetchone()

            return {
                "total_items": total_count,
                "oldest": oldest,
                "newest": newest,
                "path": str(sqlite_path),
            }, None

    except sqlite3.Error as e:
        return None, f"SQLite error: {e}"


def get_postgres_stats():
    """Get stats from PostgreSQL cache."""
    try:
        from Siphon.database.postgres.PGRES_connection import get_db_connection

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get total count
                cur.execute("SELECT COUNT(*) FROM processed_content")
                total_count = cur.fetchone()[0]

                # Get oldest and newest
                cur.execute("""
                    SELECT 
                        MIN(created_at) as oldest,
                        MAX(created_at) as newest
                    FROM processed_content
                """)
                oldest, newest = cur.fetchone()

                return {
                    "total_items": total_count,
                    "oldest": oldest,
                    "newest": newest,
                }, None

    except ImportError:
        return None, "Cannot import Siphon PostgreSQL modules"
    except Exception as e:
        return None, f"PostgreSQL error: {e}"


def check_uri_overlap():
    """Check if SQLite URIs exist in PostgreSQL."""
    sqlite_path = Path("~/.siphon/fallback_cache.db").expanduser()

    if not sqlite_path.exists():
        return None, "SQLite database does not exist"

    try:
        # Get SQLite URIs
        with sqlite3.connect(sqlite_path) as sqlite_conn:
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT uri_key FROM processed_content")
            sqlite_uris = {row[0] for row in sqlite_cursor.fetchall()}

        if not sqlite_uris:
            return {"synced": 0, "unsynced": 0, "total_sqlite": 0}, None

        # Check which ones exist in PostgreSQL
        from Siphon.database.postgres.PGRES_connection import get_db_connection

        with get_db_connection() as pg_conn:
            with pg_conn.cursor() as pg_cursor:
                # Check existence in batches
                pg_cursor.execute(
                    """
                    SELECT uri_key FROM processed_content 
                    WHERE uri_key = ANY(%s)
                """,
                    (list(sqlite_uris),),
                )

                postgres_uris = {row[0] for row in pg_cursor.fetchall()}

        synced = len(sqlite_uris & postgres_uris)  # Intersection
        unsynced = len(sqlite_uris - postgres_uris)  # SQLite only

        return {
            "synced": synced,
            "unsynced": unsynced,
            "total_sqlite": len(sqlite_uris),
        }, None

    except Exception as e:
        return None, f"Error checking overlap: {e}"


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python check_sqlite_sync.py")
        print("Checks if SQLite fallback content has been synced to PostgreSQL")
        return

    print("🔄 SQLite → PostgreSQL Sync Check")
    print("=" * 40)

    # Check SQLite
    sqlite_stats, sqlite_error = get_sqlite_stats()
    if sqlite_error:
        print(f"💾 SQLite: {sqlite_error}")
        if "does not exist" in sqlite_error:
            print("✅ No SQLite fallback data to sync")
            return
        else:
            sys.exit(1)
    else:
        print(f"💾 SQLite items: {sqlite_stats['total_items']}")

    # Check PostgreSQL
    postgres_stats, postgres_error = get_postgres_stats()
    if postgres_error:
        print(f"🐘 PostgreSQL: {postgres_error}")
        sys.exit(1)
    else:
        print(f"🐘 PostgreSQL items: {postgres_stats['total_items']}")

    # Check overlap if both exist
    if sqlite_stats["total_items"] > 0:
        overlap_stats, overlap_error = check_uri_overlap()
        if overlap_error:
            print(f"❌ {overlap_error}")
        else:
            print()
            print("📊 Sync Status:")
            print(f"   ✅ Synced: {overlap_stats['synced']}")
            print(f"   ⏳ Unsynced: {overlap_stats['unsynced']}")

            if overlap_stats["unsynced"] == 0:
                print("🎉 All SQLite content is in PostgreSQL!")
            else:
                print("⚠️  Some SQLite content not yet synced")
    else:
        print("✅ SQLite cache is empty - nothing to sync")


if __name__ == "__main__":
    main()

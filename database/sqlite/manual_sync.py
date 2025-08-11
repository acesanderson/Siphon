#!/usr/bin/env python3
"""
Manual sync script to force synchronization of SQLite items to PostgreSQL.
This handles the case where items exist in SQLite but not in PostgreSQL
and were never added to the sync queue.
"""

import sqlite3
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from Siphon.database.postgres.PGRES_processed_content import (
    cache_processed_content_direct,
)
from Siphon.data.ProcessedContent import ProcessedContent

console = Console()


def get_sqlite_connection():
    """Get SQLite database connection."""
    cache_path = Path("~/.siphon/fallback_cache.db").expanduser()
    if not cache_path.exists():
        console.print(f"[red]SQLite database not found at {cache_path}[/red]")
        return None
    return sqlite3.connect(cache_path)


def get_unsynced_items():
    """Find items in SQLite that don't exist in PostgreSQL."""
    console.print("[blue]🔍 Finding unsynced items...[/blue]")

    # Get all SQLite URIs
    sqlite_conn = get_sqlite_connection()
    if not sqlite_conn:
        return []

    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT uri_key, data FROM processed_content")
    sqlite_items = {row["uri_key"]: row["data"] for row in cursor.fetchall()}
    sqlite_conn.close()

    if not sqlite_items:
        console.print("[yellow]No items found in SQLite[/yellow]")
        return []

    # Check which ones exist in PostgreSQL
    try:
        from Siphon.database.postgres.PGRES_connection import get_db_connection

        with get_db_connection() as pg_conn:
            with pg_conn.cursor() as pg_cursor:
                # Check existence in batches
                pg_cursor.execute(
                    """
                    SELECT uri_key FROM processed_content 
                    WHERE uri_key = ANY(%s)
                    """,
                    (list(sqlite_items.keys()),),
                )
                postgres_uris = {row[0] for row in pg_cursor.fetchall()}
    except Exception as e:
        console.print(f"[red]Failed to connect to PostgreSQL: {e}[/red]")
        return []

    # Find unsynced items
    unsynced_uris = set(sqlite_items.keys()) - postgres_uris
    unsynced_items = [(uri, sqlite_items[uri]) for uri in unsynced_uris]

    console.print(f"[green]Found {len(unsynced_items)} unsynced items[/green]")
    return unsynced_items


def sync_item(uri_key: str, data_json: str) -> bool:
    """Sync a single item from SQLite to PostgreSQL."""
    try:
        # Parse the JSON data and reconstruct ProcessedContent
        import json

        data = json.loads(data_json)

        # Reconstruct ProcessedContent using the cache validation method
        processed_content = ProcessedContent.model_validate_from_cache(data)

        # Store in PostgreSQL using direct method (bypasses fallback logic)
        result = cache_processed_content_direct(processed_content)

        return True
    except Exception as e:
        console.print(f"[red]Failed to sync {uri_key}: {e}[/red]")
        return False


def main():
    console.print("[bold blue]🔄 Manual SQLite → PostgreSQL Sync[/bold blue]")
    console.print("=" * 50)

    # Find unsynced items
    unsynced_items = get_unsynced_items()

    if not unsynced_items:
        console.print("[green]✅ All items are already synced![/green]")
        return

    # Confirm before proceeding
    console.print(f"\n[yellow]Found {len(unsynced_items)} items to sync.[/yellow]")

    # Option to show items
    show_items = console.input("Show item details? (y/N): ").lower().strip()
    if show_items == "y":
        console.print("\n[dim]Unsynced items:[/dim]")
        for i, (uri, data_json) in enumerate(unsynced_items[:5], 1):
            try:
                import json

                data = json.loads(data_json)
                title = data.get("synthetic_data", {}).get("title", "Untitled")
                source_type = data.get("sourcetype", "Unknown")
                console.print(f"  {i}. [{source_type}] {title}")
            except:
                console.print(f"  {i}. {uri}")

        if len(unsynced_items) > 5:
            console.print(f"  ... and {len(unsynced_items) - 5} more")

    # Confirm sync
    proceed = (
        console.input(f"\nSync {len(unsynced_items)} items to PostgreSQL? (y/N): ")
        .lower()
        .strip()
    )
    if proceed != "y":
        console.print("[yellow]Sync cancelled.[/yellow]")
        return

    # Perform sync with progress bar
    console.print(f"\n[blue]🚀 Syncing {len(unsynced_items)} items...[/blue]")

    synced = 0
    failed = 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Syncing...", total=len(unsynced_items))

        for uri_key, data_json in unsynced_items:
            if sync_item(uri_key, data_json):
                synced += 1
            else:
                failed += 1

            progress.advance(task)

    # Results
    console.print(f"\n[bold]Sync Complete![/bold]")
    console.print(f"[green]✅ Synced: {synced}[/green]")
    if failed > 0:
        console.print(f"[red]❌ Failed: {failed}[/red]")

    # Verify results
    console.print(f"\n[blue]🔍 Verifying sync...[/blue]")
    try:
        from Siphon.database.sqlite.sync_check import check_uri_overlap

        overlap_stats, error = check_uri_overlap()

        if error:
            console.print(f"[red]Verification failed: {error}[/red]")
        else:
            console.print(f"[green]✅ Synced: {overlap_stats['synced']}[/green]")
            console.print(
                f"[yellow]⏳ Still unsynced: {overlap_stats['unsynced']}[/yellow]"
            )

            if overlap_stats["unsynced"] == 0:
                console.print(f"[bold green]🎉 All items now synced![/bold green]")
    except Exception as e:
        console.print(f"[red]Verification error: {e}[/red]")


if __name__ == "__main__":
    main()

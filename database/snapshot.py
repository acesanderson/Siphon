#!/usr/bin/env python3
"""
PostgreSQL cache snapshot utility with Rich formatting
"""

import argparse
from Siphon.database.postgres.PGRES_connection import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich.layout import Layout
from rich import box


console = Console()

# Source type styling
SOURCE_STYLES = {
    "YouTube": ("📺", "red"),
    "Article": ("📄", "blue"),
    "Doc": ("📋", "green"),
    "Image": ("🖼️", "magenta"),
    "Audio": ("🎵", "yellow"),
    "GitHub": ("🐙", "dark purple"),
    "Drive": ("💾", "cyan"),
}


def get_total_count():
    """Total cached items"""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM processed_content")
        return cur.fetchone()[0]


def format_size(chars):
    """Format character count in human readable form"""
    if chars < 1000:
        return f"{chars}"
    elif chars < 1000000:
        return f"{chars / 1000:.1f}K"
    else:
        return f"{chars / 1000000:.1f}M"


def create_header():
    """Create header panel with total count"""
    total = get_total_count()
    header_text = Text.assemble(
        ("📚 ", "bright_blue"),
        (f"{total:,}", "bold bright_white"),
        (" Total Items", "bright_blue"),
    )
    return Panel(
        header_text,
        title="[bold bright_cyan]SIPHON LIBRARY SNAPSHOT[/bold bright_cyan]",
        border_style="bright_cyan",
        box=box.DOUBLE,
    )


def create_source_distribution():
    """Create source type distribution chart"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT data->>'sourcetype' as source_type, COUNT(*) as count 
            FROM processed_content 
            GROUP BY data->>'sourcetype' 
            ORDER BY count DESC
        """)
        results = cur.fetchall()

        if not results:
            return Panel("No data found", title="Source Distribution")

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Type", width=12)
        table.add_column("Bar", min_width=20)
        table.add_column("Count", justify="right", width=6)

        max_count = max(r["count"] for r in results)

        for row in results:
            source_type = row["source_type"]
            count = row["count"]
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            # Calculate bar width (max 30 chars)
            bar_width = int((count / max_count) * 30)
            bar = "█" * bar_width

            type_text = Text.assemble((icon + " ", color), (source_type, color))
            bar_text = Text(bar, style=color)
            count_text = Text(str(count), style="bold white")

            table.add_row(type_text, bar_text, count_text)

        return Panel(
            table,
            title="[bold green]📊 Source Distribution[/bold green]",
            border_style="green",
        )


def create_recent_additions(hours=24):
    """Create recent additions panel"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cutoff = datetime.now() - timedelta(hours=hours)
        cur.execute(
            """
            SELECT data->>'sourcetype' as source_type, 
                   COALESCE(data->'synthetic_data'->>'title', 'Untitled') as title,
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
            content = Text(f"No additions in last {hours}h", style="dim")
        else:
            table = Table(show_header=False, box=None)
            table.add_column("Time", width=11)
            table.add_column("Type", width=12)
            table.add_column("Title", max_width=40)

            for row in results:
                source_type = row["source_type"]
                icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

                time_text = Text(
                    row["created_at"].strftime("%m/%d %H:%M"), style="cyan"
                )
                type_text = Text.assemble((icon + " ", color), (source_type, color))
                title = (row["title"] or "Untitled")[:40].replace("\n", " ")
                title_text = Text(title, style="white")

                table.add_row(time_text, type_text, title_text)

            content = table

        return Panel(
            content,
            title=f"[bold yellow]🕒 Recent ({hours}h)[/bold yellow]",
            border_style="yellow",
        )


def create_latest_items():
    """Create latest items panel"""
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
        table = Table(show_header=False, box=None)
        table.add_column("Time", width=11)
        table.add_column("Type", width=12)
        table.add_column("Title", max_width=70)

        for row in results:
            source_type = row["source_type"]
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            time_text = Text(
                row["created_at"].strftime("%m/%d %H:%M"), style="bright_green"
            )
            type_text = Text.assemble((icon + " ", color), (source_type, color))
            title = (row["title"] or "Untitled")[:70].replace("\n", " ")
            title_text = Text(title, style="dim")

            table.add_row(time_text, type_text, title_text)

        return Panel(
            table,
            title="[bold bright_green]⭐ Latest Items[/bold bright_green]",
            border_style="bright_green",
        )


def create_size_extremes():
    """Create size extremes panel"""
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

        table = Table(show_header=False, box=None)
        table.add_column("Size", width=8, justify="right")
        table.add_column("Type", width=12)
        table.add_column("Title", max_width=70)

        # Add largest
        for i, row in enumerate(largest):
            source_type = row["source_type"]
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            size_text = Text(f"{format_size(row['size'])} ", style="red")
            type_text = Text.assemble((icon + " ", color), (source_type, color))
            title = (row["title"] or "Untitled")[:70].replace("\n", " ")
            title_text = Text(title, style="dim")

            table.add_row(size_text, type_text, title_text)

        # Add separator
        table.add_row("", "", "")

        # Add smallest
        for row in smallest:
            source_type = row["source_type"]
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            size_text = Text(f"{format_size(row['size'])} ", style="green")
            type_text = Text.assemble((icon + " ", color), (source_type, color))
            title = (row["title"] or "Untitled")[:70].replace("\n", " ")
            title_text = Text(title, style="dim")

            table.add_row(size_text, type_text, title_text)

        return Panel(
            table,
            title="[bold magenta]📏 Size Extremes[/bold magenta]",
            border_style="magenta",
        )


def search_by_source_type(source_type):
    """Show items for specific source type"""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT COALESCE(data->'synthetic_data'->>'title', 'Untitled') as title,
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
            console.print(f"[red]No {source_type} items found[/red]")
            return

        icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

        table = Table(show_header=True, box=box.MINIMAL)
        table.add_column("Date", width=11)
        table.add_column("Title", max_width=60)

        for row in results:
            date_text = row["created_at"].strftime("%m/%d %H:%M")
            title = (row["title"] or "Untitled")[:60]
            table.add_row(date_text, title)

        panel = Panel(
            table,
            title=f"[bold {color}]{icon} {source_type} Items ({len(results)})[/bold {color}]",
            border_style=color,
        )
        console.print(panel)


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL cache snapshot")
    parser.add_argument("--source-type", help="Show items for specific source type")
    parser.add_argument(
        "--recent", type=int, default=24, help="Recent hours (default: 24)"
    )

    args = parser.parse_args()

    if args.source_type:
        search_by_source_type(args.source_type)
        return

    # Default overview
    console.print(create_header())
    console.print()
    console.print(create_source_distribution())
    console.print()
    console.print(create_recent_additions(args.recent))
    console.print()
    console.print(create_latest_items())
    console.print()
    console.print(create_size_extremes())


if __name__ == "__main__":
    main()

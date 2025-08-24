"""
PostgreSQL cache snapshot utility with Rich formatting
"""

from Siphon.database.postgres.PGRES_connection import get_db_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
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


def generate_snapshot_for_list(corpus_list: list, console: Console = console):
    """Generate snapshot for in-memory corpus list"""

    def create_header():
        """Create header panel with total count"""
        header_text = Text.assemble(
            ("📚 ", "bright_blue"),
            (f"{len(corpus_list):,}", "bold bright_white"),
            (" Items in Corpus", "bright_blue"),
        )
        return Panel(
            header_text,
            title="[bold bright_cyan]CORPUS SNAPSHOT[/bold bright_cyan]",
            border_style="bright_cyan",
            box=box.DOUBLE,
        )

    def create_source_distribution():
        """Create source type distribution chart"""
        # Count by source type
        source_counts = {}
        for item in corpus_list:
            source_type = item.uri.sourcetype.value
            source_counts[source_type] = source_counts.get(source_type, 0) + 1

        if not source_counts:
            return Panel("No data found", title="Source Distribution")

        # Sort by count descending
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Type", width=12)
        table.add_column("Bar", min_width=20)
        table.add_column("Count", justify="right", width=6)

        max_count = max(source_counts.values())

        for source_type, count in sorted_sources:
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

    def create_latest_items():
        """Create latest items panel - shows first 3 items"""
        # Take first 3 items (no timestamp sorting available)
        latest_items = corpus_list[:3]

        if not latest_items:
            content = Text("No items available", style="dim")
        else:
            table = Table(show_header=False, box=None)
            table.add_column("Index", width=8)
            table.add_column("Type", width=12)
            table.add_column("Title", max_width=70)

            for i, item in enumerate(latest_items, 1):
                source_type = item.uri.sourcetype.value
                icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

                index_text = Text(f"#{i}", style="bright_green")
                type_text = Text.assemble((icon + " ", color), (source_type, color))
                title = (item.title or "Untitled")[:70].replace("\n", " ")
                title_text = Text(title, style="dim")

                table.add_row(index_text, type_text, title_text)

            content = table

        return Panel(
            content,
            title="[bold bright_green]⭐ Sample Items[/bold bright_green]",
            border_style="bright_green",
        )

    def create_size_extremes():
        """Create size extremes panel"""
        if not corpus_list:
            return Panel("No items available", title="Size Extremes")

        # Calculate sizes and sort
        items_with_sizes = []
        for item in corpus_list:
            context_length = len(item.context) if item.context else 0
            items_with_sizes.append((item, context_length))

        # Sort by size
        items_with_sizes.sort(key=lambda x: x[1], reverse=True)

        # Get largest 3 and smallest 3
        largest = items_with_sizes[:3]
        smallest = items_with_sizes[-3:] if len(items_with_sizes) > 3 else []

        table = Table(show_header=False, box=None)
        table.add_column("Size", width=8, justify="right")
        table.add_column("Type", width=12)
        table.add_column("Title", max_width=70)

        # Add largest
        for item, size in largest:
            source_type = item.uri.sourcetype.value
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            size_text = Text(f"{format_size(size)} ", style="red")
            type_text = Text.assemble((icon + " ", color), (source_type, color))
            title = (item.title or "Untitled")[:70].replace("\n", " ")
            title_text = Text(title, style="dim")

            table.add_row(size_text, type_text, title_text)

        # Add separator if we have both largest and smallest
        if smallest:
            table.add_row("", "", "")

        # Add smallest
        for item, size in smallest:
            source_type = item.uri.sourcetype.value
            icon, color = SOURCE_STYLES.get(source_type, ("📁", "white"))

            size_text = Text(f"{format_size(size)} ", style="green")
            type_text = Text.assemble((icon + " ", color), (source_type, color))
            title = (item.title or "Untitled")[:70].replace("\n", " ")
            title_text = Text(title, style="dim")

            table.add_row(size_text, type_text, title_text)

        return Panel(
            table,
            title="[bold magenta]📏 Size Extremes[/bold magenta]",
            border_style="magenta",
        )

    def create_content_summary():
        """Create a summary of content types and characteristics"""
        # Count items with various attributes
        with_titles = sum(1 for item in corpus_list if item.title)
        with_descriptions = sum(1 for item in corpus_list if item.description)
        with_summaries = sum(1 for item in corpus_list if item.summary)
        with_tags = sum(1 for item in corpus_list if item.tags)

        total_context_chars = sum(
            len(item.context) for item in corpus_list if item.context
        )
        avg_context_size = total_context_chars // len(corpus_list) if corpus_list else 0

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", width=20)
        table.add_column("Value", width=15, justify="right")
        table.add_column("Percentage", width=10, justify="right")

        metrics = [
            ("Items with titles", with_titles),
            ("Items with descriptions", with_descriptions),
            ("Items with summaries", with_summaries),
            ("Items with tags", with_tags),
        ]

        for metric_name, count in metrics:
            percentage = (
                f"{(count / len(corpus_list) * 100):.1f}%" if corpus_list else "0%"
            )
            table.add_row(
                Text(metric_name, style="cyan"),
                Text(str(count), style="white"),
                Text(percentage, style="dim"),
            )

        # Add average size row
        table.add_row("", "", "")  # Separator
        table.add_row(
            Text("Avg context size", style="cyan"),
            Text(format_size(avg_context_size), style="white"),
            Text("", style="dim"),
        )

        return Panel(
            table,
            title="[bold blue]📈 Content Summary[/bold blue]",
            border_style="blue",
        )

    # Generate the full snapshot
    if not corpus_list:
        console.print(
            Panel("Empty corpus - no items to display", title="Corpus Snapshot")
        )
        return

    console.print(create_header())
    console.print()
    console.print(create_source_distribution())
    console.print()
    console.print(create_content_summary())
    console.print()
    console.print(create_latest_items())
    console.print()
    console.print(create_size_extremes())


def generate_snapshot_for_library(console: Console = console):
    # Default overview
    console.print(create_header())
    console.print()
    console.print(create_source_distribution())
    console.print()
    console.print(create_recent_additions())
    console.print()
    console.print(create_latest_items())
    console.print()
    console.print(create_size_extremes())


def generate_snapshot(
    console: Console = console, corpus_list: list | None = None, library: bool = True
):
    if library:
        generate_snapshot_for_library(console)
    elif corpus_list:
        generate_snapshot_for_list(corpus_list, console)
    else:
        console.print(
            "[red]Error: Must specify either library=True or submit a corpus_list[/red]"
        )


def main():
    generate_snapshot_for_library()


if __name__ == "__main__":
    from Siphon.collections.corpus.siphon_corpus import CorpusFactory

    # Create a corpus and convert to list
    corpus = CorpusFactory.from_library()
    corpus_list = list(corpus)

    # Generate snapshot
    generate_snapshot_for_list(corpus_list)

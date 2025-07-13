"""
Rich display mixin for ProcessedContent.

Usage:
    from Siphon.display.processed_content_display import ProcessedContentDisplayMixin

    class ProcessedContent(ProcessedContentDisplayMixin, BaseModel):
        # ... your existing fields ...
        pass

    # Then use:
    processed_content.pretty_print()
"""

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime


class ProcessedContentDisplayMixin:
    """Mixin to add Rich display capabilities to ProcessedContent."""

    def pretty_print(self) -> None:
        """Display ProcessedContent in a beautiful, structured format."""
        console = Console()

        # Header
        console.print(self._header_panel())
        console.print()

        # Two-column layout: URI + Metadata
        console.print(Columns([self._uri_panel(), self._metadata_panel()], equal=True))
        console.print()

        # Context preview
        console.print(self._context_panel())
        console.print()

        # Synthetic data (if available)
        if self.synthetic_data:
            console.print(self._synthetic_panel())
            console.print()

    def _header_panel(self) -> Panel:
        """Main header with title and URI."""
        title = (
            self.title if self.title else f"Content from {self.uri.sourcetype.value}"
        )

        content = Text()
        content.append(title, style="bold bright_blue")
        content.append(f"\n📍 {self.uri.uri}", style="dim")

        return Panel(content, box=box.DOUBLE, style="bright_blue", padding=(1, 2))

    def _uri_panel(self) -> Panel:
        """URI details panel."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="cyan bold", width=12)
        table.add_column("Value", style="white")

        table.add_row(
            "Source Type", f"[bright_green]{self.uri.sourcetype.value}[/bright_green]"
        )
        table.add_row("Original", f"[yellow]{self.uri.source}[/yellow]")
        table.add_row("URI", f"[blue]{self.uri.uri}[/blue]")

        return Panel(
            table, title="[bold cyan]🔗 URI[/bold cyan]", box=box.ROUNDED, style="cyan"
        )

    def _context_panel(self) -> Panel:
        """Context preview panel."""
        context_text = self.llm_context.context
        word_count = len(context_text.split())
        char_count = len(context_text)

        # Show preview (first 400 chars)
        preview = (
            context_text[:400] + "..." if len(context_text) > 400 else context_text
        )

        content = Text(preview, style="white")
        content.append(f"\n\n({word_count:,} words, {char_count:,} chars)", style="dim")

        return Panel(
            content,
            title="[bold green]📄 Content[/bold green]",
            box=box.ROUNDED,
            style="green",
        )

    def _metadata_panel(self) -> Panel:
        """Metadata panel with context-specific info."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bright_white bold", width=12)
        table.add_column("Value", style="white")

        context = self.llm_context

        # File-based metadata
        if hasattr(context, "file_path"):
            from pathlib import Path

            file_path = Path(context.file_path)
            table.add_row("File", f"[yellow]{file_path.name}[/yellow]")

            if hasattr(context, "file_size"):
                size_mb = context.file_size / (1024 * 1024)
                table.add_row("Size", f"[white]{size_mb:.1f} MB[/white]")

            if hasattr(context, "content_modified_at"):
                mod_time = datetime.fromtimestamp(context.content_modified_at)
                table.add_row(
                    "Modified", f"[white]{mod_time.strftime('%Y-%m-%d')}[/white]"
                )

        # Online metadata
        elif hasattr(context, "url"):
            if hasattr(context, "domain"):
                table.add_row("Domain", f"[yellow]{context.domain}[/yellow]")

            # YouTube specifics
            if hasattr(context, "channel"):
                table.add_row("Channel", f"[bright_red]{context.channel}[/bright_red]")
            if hasattr(context, "duration"):
                duration = f"{context.duration // 60}:{context.duration % 60:02d}"
                table.add_row("Duration", f"[white]{duration}[/white]")
            if hasattr(context, "view_count"):
                table.add_row("Views", f"[white]{context.view_count:,}[/white]")

            # GitHub specifics
            if hasattr(context, "stars"):
                table.add_row("Stars", f"[yellow]⭐ {context.stars:,}[/yellow]")
            if hasattr(context, "language"):
                table.add_row(
                    "Language", f"[bright_blue]{context.language}[/bright_blue]"
                )

        return Panel(
            table,
            title="[bold bright_white]📊 Metadata[/bold bright_white]",
            box=box.ROUNDED,
            style="bright_white",
        )

    def _synthetic_panel(self) -> Panel:
        """AI-generated synthetic data panel."""
        if not self.synthetic_data:
            return Panel(
                Text("No synthetic data", style="dim"),
                title="[bold magenta]🤖 AI Data[/bold magenta]",
                style="magenta",
            )

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="magenta bold", width=12)
        table.add_column("Value", style="white")

        sd = self.synthetic_data

        if sd.title:
            table.add_row("Title", f"[bright_yellow]{sd.title}[/bright_yellow]")

        if sd.description:
            desc = (
                sd.description[:80] + "..."
                if len(sd.description) > 80
                else sd.description
            )
            table.add_row("Description", f"[white]{desc}[/white]")

        if sd.summary:
            # words = len(sd.summary.split())
            table.add_row("Summary", f"[white]{sd.summary} words[/white]")

        if sd.topics:
            topics = ", ".join(sd.topics[:3])
            if len(sd.topics) > 3:
                topics += f" (+{len(sd.topics) - 3})"
            table.add_row("Topics", f"[bright_cyan]{topics}[/bright_cyan]")

        if sd.entities:
            entities = ", ".join(sd.entities[:3])
            if len(sd.entities) > 3:
                entities += f" (+{len(sd.entities) - 3})"
            table.add_row("Entities", f"[bright_red]{entities}[/bright_red]")

        return Panel(
            table,
            title="[bold magenta]🤖 AI Data[/bold magenta]",
            box=box.ROUNDED,
            style="magenta",
        )

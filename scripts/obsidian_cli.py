"""
Obsidian as a SourceType implementation is pending; in the meanwhile a convenience (non-persistant) CLI for Obsidian is provided.
Immediate use:
- return context from a set of daily notes for a given date range
"""

from pathlib import Path
import argparse

obsidian_vault = Path("~/MorphyMobile").expanduser()

# Glob all date notes (filename: YYYY-MM-DD.md) in the vault
date_notes = sorted(obsidian_vault.glob("202[0-9]-[0-1][0-9]-[0-3][0-9].md"))


def get_date_notes(start_date, end_date) -> str:
    """Get date notes between start_date and end_date (inclusive)."""
    selected_notes = []
    for note in date_notes:
        note_date_str = note.stem  # Get the filename without extension
        if start_date <= note_date_str <= end_date:
            selected_notes.append(note)
    llm_context = ""
    for note in selected_notes:
        llm_context += f"\n\n# {note.stem}\n"
        llm_context += note.read_text()
    return llm_context


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Obsidian date notes for a given date range."
    )
    # Print usage example
    parser.epilog = "Example usage: python obsidian_cli.py 2023-10-01 2023-10-07"
    parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    context = get_date_notes(args.start_date, args.end_date)
    print(context)


if __name__ == "__main__":
    main()

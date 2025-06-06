"""
CRUD functions for Siphon project. Adapted from Kramer.database.

We will use this database as a cache for siphon data, keyed to file hashes.
"""

from Siphon.ProcessedFile import ProcessedFile
from Siphon.database.PGRES_connection import get_db_connection
from rich.console import Console

console = Console()


# Create table
def create_table():
    """
    Create a table in the database.
    Table name = siphon
    Three columns:
    - sha256 (text) - primary key
    - abs_path (text) - absolute path to the file
    - llm_context (text) - LLM context for the file
    """
    query = "CREATE TABLE IF NOT EXISTS siphon (sha256 TEXT PRIMARY KEY, abs_path TEXT, llm_context TEXT);"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        console.print("[cyan]siphon table created successfully.[/cyan]")


# Add/Update record
def insert_siphon(siphon: ProcessedFile):
    """
    Insert or update a record in the siphon table.

    Args:
        siphon (ProcessedFile): ProcessedFile object to insert or update
    """
    # Get vars
    sha256 = siphon.sha256
    abs_path = siphon.abs_path
    llm_context = siphon.llm_context
    # Insert or update record
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO siphon (sha256, abs_path, llm_context) VALUES (%s, %s, %s)",
            (sha256, abs_path, llm_context),
        )
        conn.commit()
        console.print(f"[green]siphon {abs_path} saved successfully.[/green]")


def get_siphon_by_hash(sha256: str) -> str | None:
    """
    Get the tools Counter for a specific course.

    Args:
        sha256 (str): SHA-256 hash of the file

    Returns:
        str | None: LLM context if found, else None
    """
    # Query for the record
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT llm_context FROM siphon WHERE sha256 = %s",
            (sha256,),
        )
        result = cursor.fetchone()

        if result is None:
            return None

        # Convert JSON to Counter
        return result[0]


def get_all_siphon() -> list[ProcessedFile] | None:
    """
    Get all tools for all courses.

    Returns:
        dict: Dictionary mapping course_admin_id to Counter objects
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sha256, abs_path, llm_context FROM siphon")
        results = cursor.fetchall()

        if not results:
            return None
        # Convert results to list of ProcessedFile objects
        siphon = [
            ProcessedFile(sha256=row[0], abs_path=row[1], llm_context=row[2])
            for row in results
        ]
        return siphon


def clear_table():
    """
    Clear all data from the tools table.
    Only use this manually.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM siphon")
        conn.commit()
        console.print("[yellow]siphon table cleared successfully.[/yellow]")


def delete_table():
    """
    Delete the tools table entirely.
    Only use this manually.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS siphon")
        conn.commit()
        console.print("[yellow]siphon table deleted successfully.[/yellow]")

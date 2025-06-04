"""
CRUD functions for Siphon project. Adapted from Kramer.database.

We will use this database as a cache for siphon data, keyed to file hashes.
"""

from PGRES_connection import get_db_connection
from pathlib import Path
from rich.console import Console
from collections import Counter
import json

console = Console()
dir_path = Path(__file__).parent


# Create table
def create_table():
    """
    Create a table in the database.
    Table name = tools
    Two columns:
    - course_admin_id (int)
    - tools_counter (jsonb) - stores a Python Counter object
    """
    query = "CREATE TABLE IF NOT EXISTS tools (course_admin_id INT PRIMARY KEY, tools_counter JSONB);"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        console.print("[cyan]Tools table created successfully.[/cyan]")


# Add/Update record
def insert_tools(course_admin_id: int, tools_counter: Counter):
    """
    Insert or update a tools Counter object for a specific course.

    Args:
        course_admin_id (int): The course identifier
        tools_counter (Counter): Counter object with tool frequencies
    """
    # Convert Counter to dict, then to JSON string
    tools_json = json.dumps(dict(tools_counter))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tools (course_admin_id, tools_counter) VALUES (%s, %s) "
            "ON CONFLICT (course_admin_id) DO UPDATE SET tools_counter = EXCLUDED.tools_counter;",
            (course_admin_id, tools_json),
        )
        conn.commit()
        console.print(
            f"[green]Tools for course {course_admin_id} saved successfully.[/green]"
        )


def get_tools_by_course_id(course_admin_id: int) -> Counter | None:
    """
    Get the tools Counter for a specific course.

    Args:
        course_admin_id (int): The course identifier

    Returns:
        Counter or None: Counter object with tool frequencies, None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tools_counter FROM tools WHERE course_admin_id = %s",
            (course_admin_id,),
        )
        result = cursor.fetchone()

        if result is None:
            return None

        # Convert JSON to Counter
        return Counter(result[0])


def get_all_tools() -> dict[int, Counter]:
    """
    Get all tools for all courses.

    Returns:
        dict: Dictionary mapping course_admin_id to Counter objects
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT course_admin_id, tools_counter FROM tools")
        results = cursor.fetchall()

        if not results:
            return {}

        # Convert results to dict of Counters
        return {row[0]: Counter(row[1]) for row in results}


def get_all_course_ids() -> list[int]:
    """
    Get all course admin IDs.

    Returns:
        list: List of all course admin IDs
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT course_admin_id FROM tools")
        results = cursor.fetchall()
        return [row[0] for row in results]


def get_courses_using_tool(tool_name: str) -> list[int]:
    """
    Find all courses that use a specific tool.

    Args:
        tool_name (str): The name of the tool to search for

    Returns:
        list: List of course admin IDs that use the tool
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT course_admin_id FROM tools WHERE tools_counter ? %s", (tool_name,)
        )
        results = cursor.fetchall()
        return [row[0] for row in results]


def get_popular_tools(limit: int = 10) -> Counter:
    """
    Get the most popular tools across all courses.

    Args:
        limit (int): Limit the number of results

    Returns:
        Counter: Counter object with aggregated tool frequencies
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tools_counter FROM tools")
        results = cursor.fetchall()

        if not results:
            return Counter()

        # Aggregate all counters
        combined_counter = Counter()
        for row in results:
            combined_counter.update(Counter(row[0]))

        # Return most common
        return Counter(dict(combined_counter.most_common(limit)))


def clear_table():
    """
    Clear all data from the tools table.
    Only use this manually.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tools")
        conn.commit()
        console.print("[yellow]Tools table cleared successfully.[/yellow]")


def delete_table():
    """
    Delete the tools table entirely.
    Only use this manually.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tools")
        conn.commit()
        console.print("[yellow]Tools table deleted successfully.[/yellow]")

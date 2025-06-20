"""
CRUD functions for Siphon project. Adapted from Kramer.database.

We will use this database as a cache for siphon data, keyed to file hashes.
"""

from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.database.postgres.PGRES_connection import get_db_connection
from Siphon.data.URI import URI
from Siphon.data.SyntheticData import SyntheticData
from Siphon.data.Metadata import SiphonMetadata
from rich.console import Console

console = Console()

"""
class ProcessedContent(BaseModel):
    # Primary identifiers
    content_id: str = Field(
        ..., description="Unique identifier for the content, a hash or doc ID"
    )
    uri: URI = Field(
        ..., description="Original URI of the content, used for retrieval"
    )

    # Temporal data (as Unix timestamps)
    ## Record-specific time stamps
    ingested_at: int
    last_updated_at: int

    # Core processed data
    llm_context: str = Field(
        ..., description="Processed content ready for LLM consumption"
    )

    # Synthetic data (title, description, summary, topics, entities) -- added post init
    synthetic_data: Optional[SyntheticData] = Field(
        default=None, description="AI-generated enrichments applied to the content"
    )

    # Source-specific metadata (typed)
    metadata: SiphonMetadata = Field(
        default_factory=SiphonMetadata,
        description="Source-specific metadata, such as file size, author, etc.",
    )
"""
"""
class URI(BaseModel):
    source: str = Field(..., description="The original source URL, filepath, etc.")
    source_type: SourceType = Field(..., description="The type of source this URI represents.")
    uri: str = Field(..., description="The URI string representation of the source.")

"""
"""
class SyntheticData(BaseModel):
    ""
    AI-generated enrichments, applied as a "finishing step" to the content.
    ""

    title: str = Field(
        default="", description="Title of the content, either extracted or generated"
    )
    description: str = Field(
        default="", description="Short description or summary of the content"
    )
    summary: str = Field(default="", description="Detailed summary of the content")
    topics: list[str] = Field(
        default_factory=list,
        description="List of topics or keywords associated with the content, an area liable to change with cluster analyses.",
    )
    entities: list[str] = Field(
        default_factory=list,
        description="List of entities (people, places, organizations) mentioned in the content.",
    )
"""



# Create table
def create_table():
    """
    Create a table in the database.
    Table name = siphon
    Columns correspond to ProcessedContent fields:
    - content_id: SHA-256 hash of the file
    - uri: a pydantic URI object with three fields:
        - source: the original source URL, filepath, etc.
        - source_type: the type of source this URI represents (e.g., obsidian, file, youtube, drive, etc.)
        - uri: the URI string representation of the source
    - ingested_at: Unix timestamp of when the content was ingested
    - last_updated_at: Unix timestamp of the last update to the content
    - llm_context: the processed content ready for LLM consumption
    - synthetic_data: AI-generated enrichments applied to the content (optional)
        - title: Title of the content, either extracted or generated
        - description: Short description or summary of the content
        - metadata: Source-specific metadata, such as file size, author, etc.
        - topics: List of topics or keywords associated with the content
        - entities: List of entities (people, places, organizations) mentioned in the content
    - metadata: Source-specific metadata, such as file size, author, etc. Multiple potential pydantic models could be used here, depending on the source type.
    """
    query = """CREATE TABLE IF NOT EXISTS siphon (
        content_id TEXT PRIMARY KEY,
        URI JSONB,
        llm_context TEXT NOT NULL,
        ingested_at BIGINT NOT NULL,
        last_updated_at BIGINT NOT NULL,
        synthetic_data JSONB,
        metadata JSONB
    )"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        console.print("[cyan]siphon table created successfully.[/cyan]")


# Add/Update record
def insert_siphon(siphon: ProcessedContent):
    """
    Insert or update a record in the siphon table.

    Args:
        siphon (ProcessedContent): ProcessedContent object to insert or update
    """
    # Get vars
    content_id = siphon.content_id
    uri = siphon.uri
    llm_context = siphon.llm_context
    ingested_at = siphon.ingested_at
    last_updated_at = siphon.last_updated_at
    synthetic_data = siphon.synthetic_data
    metadata = siphon.metadata
    # Insert or update record
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO siphon (content_id, URI, llm_context, ingested_at, last_updated_at, synthetic_data, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (content_id) DO UPDATE SET \
                URI = EXCLUDED.URI, llm_context = EXCLUDED.llm_context, ingested_at = EXCLUDED.ingested_at, \
                last_updated_at = EXCLUDED.last_updated_at, synthetic_data = EXCLUDED.synthetic_data, metadata = EXCLUDED.metadata",
            (
                content_id,
                uri.model_dump(),
                llm_context,
                ingested_at,
                last_updated_at,
                synthetic_data.model_dump() if synthetic_data else None,
                metadata.model_dump(),
            )
        )
        conn.commit()
        console.print(f"[green]siphon {siphon.uri.uri} saved successfully.[/green]")

def get_siphon_by_id(id: str) -> str | None:
    """
    """
    # Query for the record
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT llm_context FROM siphon WHERE content_id = %s",
            (id,),
        )
        result = cursor.fetchone()

        if result is None:
            return None

        # Convert JSON to Counter
        return result[0]


def get_all_siphon() -> list[ProcessedContent] | None:
    """
    Get all tools for all courses.

    Returns:
        dict: Dictionary mapping course_admin_id to Counter objects
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM siphon")
        results = cursor.fetchall()

        if not results:
            return None
        # Convert results to list of ProcessedContent objects
        siphon = [
            ProcessedContent(
                content_id=row[0],
                uri=URI(**row[1]),
                llm_context=row[2],
                ingested_at=row[3],
                last_updated_at=row[4],
                synthetic_data=SyntheticData(**row[5] if row[5] else None),
                metadata=SiphonMetadata(**row[6])
            )
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
        console.print("[yellow]siphon table deleted uccessfully.[/yellow]")

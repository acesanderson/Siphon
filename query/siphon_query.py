from Siphon.database.postgres.PGRES_connection import get_db_connection
from Siphon.data.ProcessedContent import ProcessedContent
from Siphon.logs.logging_config import get_logger
from psycopg2.extras import RealDictCursor

logger = get_logger(__name__)


class SiphonQuery:
    """
    A class to handle siphon queries.
    """

    def __init__(self, get_db_connection=get_db_connection):
        """
        Initializes the SiphonQuery instance.
        Has our own get_db_connection function as a default parameter.
        """
        self.get_db_connection = get_db_connection

    def last(self) -> ProcessedContent | None:
        """
        Queries the latest processed content from the database.
        Returns a ProcessedContent instance or None if no content is found.
        """

        with (
            get_db_connection() as conn,
            conn.cursor(cursor_factory=RealDictCursor) as cur,
        ):
            cur.execute("""
                    SELECT data FROM processed_content 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """)

            row = cur.fetchone()
            if not row:
                return None

            try:
                return ProcessedContent.model_validate_from_cache(row["data"])
            except Exception as e:
                logger.error(f"Failed to deserialize latest cached content: {e}")
                return None


if __name__ == "__main__":
    sq = SiphonQuery()
    last = sq.last()
    print(last)

"""
This script from 2025-08-25 updates existing records in the `processed_content` table to new schema requirements:
- Adds `created_at` and `updated_at` timestamps to the JSONB `data` field.
- Generates and populates `description_embedding` and `summary_embedding` vector fields using the `all-MiniLM-L6-v2` model from SentenceTransformers.
"""

from siphon.database.postgres.PGRES_connection import get_db_connection
from siphon.data.processed_content import ProcessedContent
from psycopg2.extras import RealDictCursor, Json


def migrate_existing_library():
    from sentence_transformers import SentenceTransformer
    from tqdm import tqdm
    import time

    model = SentenceTransformer("all-MiniLM-L6-v2")

    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get all records
        cur.execute(
            "SELECT id, data, created_at, updated_at FROM processed_content ORDER BY id"
        )
        records = cur.fetchall()

        print(f"Migrating {len(records)} records...")

        for record in tqdm(records):
            try:
                # Reconstruct ProcessedContent
                content = ProcessedContent.model_validate_from_cache(record["data"])

                # Add timestamps to the object
                content.created_at = int(record["created_at"].timestamp())
                content.updated_at = int(record["updated_at"].timestamp())

                # Generate embeddings
                desc_embedding = None
                summary_embedding = None

                if content.synthetic_data:
                    try:
                        if content.synthetic_data.description:
                            desc_embedding = model.encode(
                                content.synthetic_data.description
                            ).tolist()
                    except:
                        pass
                    try:
                        if content.synthetic_data.summary:
                            summary_embedding = model.encode(
                                content.synthetic_data.summary
                            ).tolist()
                    except:
                        pass

                # Update both JSONB data (with timestamps) and vector columns
                updated_data = content.model_dump_for_cache()
                cur.execute(
                    """
                    UPDATE processed_content 
                    SET data = %s, 
                        description_embedding = %s, 
                        summary_embedding = %s
                    WHERE id = %s
                """,
                    (
                        Json(updated_data),
                        desc_embedding,
                        summary_embedding,
                        record["id"],
                    ),
                )

                if record["id"] % 50 == 0:
                    conn.commit()

            except Exception as e:
                print(f"Failed to migrate record {record['id']}: {e}")
                continue

        conn.commit()
        print("Migration complete! Now creating indexes...")

        # Create indexes after data is populated
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_description_embedding 
            ON processed_content USING hnsw (description_embedding vector_cosine_ops);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_summary_embedding 
            ON processed_content USING hnsw (summary_embedding vector_cosine_ops);
        """)

        conn.commit()
        print("Indexes created! Migration fully complete.")


if __name__ == "__main__":
    migrate_existing_library()

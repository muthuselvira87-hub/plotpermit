
import json

from pgvector.psycopg import register_vector

from app.database import get_db_connection


EMBEDDINGS_FILE = "data/processed/embeddings.jsonl"


def create_embeddings_table():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;

                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding VECTOR(768) NOT NULL
                );
            """)

        connection.commit()
        print("Embeddings table is ready!")

    finally:
        connection.close()


def insert_embeddings():
    connection = get_db_connection()

    try:
        register_vector(connection)

        inserted = 0
        skipped = 0
        cleaned = 0

        with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as file:
            with connection.cursor() as cursor:

                for line in file:
                    record = json.loads(line)

                    # Remove invisible NUL characters
                    chunk_id = record["chunk_id"].replace("\x00", "")
                    source = record["source"].replace("\x00", "")
                    text = record["text"].replace("\x00", "")

                    if (
                        chunk_id != record["chunk_id"]
                        or source != record["source"]
                        or text != record["text"]
                    ):
                        cleaned += 1

                    cursor.execute("""
                        INSERT INTO document_embeddings
                        (chunk_id, source, page_number,
                         chunk_index, text, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (chunk_id) DO NOTHING
                    """, (
                        chunk_id,
                        source,
                        record["page_number"],
                        record["chunk_index"],
                        text,
                        record["embedding"]
                    ))

                    if cursor.rowcount == 1:
                        inserted += 1
                    else:
                        skipped += 1

        connection.commit()

        print("\n========== DATABASE INSERTION ==========")
        print("New embeddings inserted:", inserted)
        print("Existing embeddings skipped:", skipped)
        print("Records cleaned:", cleaned)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_embeddings_table()
    insert_embeddings()

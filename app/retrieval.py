
from google import genai
from pgvector import Vector
from pgvector.psycopg import register_vector

from app.config import get_settings
from app.database import get_db_connection

# Embedding configuration
MODEL_NAME = "gemini-embedding-001"
DIMENSIONS = 768

# Retrieval configuration
TOP_K = 5
DISTANCE_THRESHOLD = 0.30


def generate_query_embedding(question: str) -> list:
    """Convert the user's question into a vector."""

    settings = get_settings()

    if not settings.gemini_api_key:
        raise ValueError("Gemini API key is missing")

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=question,
        config={
            "task_type": "RETRIEVAL_QUERY",
            "output_dimensionality": DIMENSIONS
        }
    )

    if not response.embeddings:
        raise ValueError("Gemini returned no query embedding")

    vector = response.embeddings[0].values

    if len(vector) != DIMENSIONS:
        raise ValueError("Unexpected embedding dimensions")

    return vector


def retrieve_relevant_chunks(question: str) -> list:
    """Find relevant document chunks using PostgreSQL and pgvector."""

    # Generate query embedding
    query_vector = Vector(
        generate_query_embedding(question)
    )

    connection = get_db_connection()

    try:
        register_vector(connection)

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    source,
                    page_number,
                    text,
                    embedding <=> %s AS distance
                FROM document_embeddings
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (
                    query_vector,
                    query_vector,
                    TOP_K
                )
            )

            rows = cursor.fetchall()

        results = []

        for row in rows:
            results.append({
                "chunk_id": row[0],
                "source": row[1],
                "page_number": row[2],
                "text": row[3],
                "distance": float(row[4])
            })

        # Filter out weakly matching document chunks
        relevant_results = [
            result
            for result in results
            if result["distance"] <= DISTANCE_THRESHOLD
        ]

        print("\n========== RETRIEVAL RESULTS ==========")
        print("Question:", question)
        print("Chunks retrieved:", len(results))
        print("Relevant chunks:", len(relevant_results))
        print("Distance threshold:", DISTANCE_THRESHOLD)

        return relevant_results

    finally:
        connection.close()


if __name__ == "__main__":

    question = (
        "What is the purpose of the Tamil Nadu "
        "Combined Development and Building Rules, 2019?"
    )

    chunks = retrieve_relevant_chunks(question)

    for chunk in chunks:
        print("\nSource:", chunk["source"])
        print("Page:", chunk["page_number"])
        print("Distance:", round(chunk["distance"], 4))
        print("Content:", chunk["text"][:300])

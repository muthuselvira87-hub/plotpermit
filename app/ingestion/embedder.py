
import json
import time
from pathlib import Path

from google import genai

from app.config import get_settings


# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "chunks.jsonl"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "embeddings.jsonl"


# Embedding configuration
MODEL_NAME = "gemini-embedding-001"
DIMENSIONS = 768
BATCH_SIZE = 8
BATCH_DELAY = 10
MAX_RETRIES = 10


def load_completed_ids():
    """Load already generated chunk IDs to support resuming."""

    completed = set()

    if not OUTPUT_FILE.exists():
        return completed

    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            completed.add(record["chunk_id"])

    return completed


def generate_embeddings(client, texts):
    """Generate embeddings with automatic retry handling."""

    for attempt in range(MAX_RETRIES):

        try:
            response = client.models.embed_content(
                model=MODEL_NAME,
                contents=texts,
                config={
                    "task_type": "RETRIEVAL_DOCUMENT",
                    "output_dimensionality": DIMENSIONS
                }
            )

            if not response.embeddings:
                raise ValueError("The API returned no embeddings.")

            if len(response.embeddings) != len(texts):
                raise ValueError(
                    "Embedding count does not match input count."
                )

            vectors = [
                embedding.values
                for embedding in response.embeddings
            ]

            for vector in vectors:
                if len(vector) != DIMENSIONS:
                    raise ValueError(
                        "Unexpected embedding dimensions."
                    )

            return vectors

        except Exception as error:

            status_code = getattr(error, "status_code", None)

            # Handle Gemini quota errors
            if status_code == 429:

                wait_seconds = min(65 * (attempt + 1), 300)

                print(
                    f"API quota reached. "
                    f"Waiting {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)
                continue

            # Handle other temporary errors
            if attempt == MAX_RETRIES - 1:
                raise

            wait_seconds = min(2 ** (attempt + 1), 30)

            print(
                f"Request failed. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        "Embedding generation failed after maximum retries."
    )


def main():

    settings = get_settings()

    if not settings.gemini_api_key:
        raise ValueError(
            "Gemini API key is missing from .env"
        )

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {INPUT_FILE}"
        )

    # Create Gemini client
    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    # Load existing embeddings
    completed_ids = load_completed_ids()

    # Read all chunks
    with INPUT_FILE.open("r", encoding="utf-8") as input_file:

        chunks = [
            json.loads(line)
            for line in input_file
            if line.strip()
        ]

    # Find chunks that still need embeddings
    pending_chunks = [
        chunk for chunk in chunks
        if chunk["chunk_id"] not in completed_ids
    ]

    print("\n========== EMBEDDING PROCESS ==========")

    print(f"Total chunks: {len(chunks)}")
    print(f"Already completed: {len(completed_ids)}")
    print(f"Remaining chunks: {len(pending_chunks)}")

    processed = 0

    # Process chunks in batches
    for start in range(0, len(pending_chunks), BATCH_SIZE):

        batch = pending_chunks[
            start:start + BATCH_SIZE
        ]

        texts = [
            chunk["text"]
            for chunk in batch
        ]

        # Generate vectors
        vectors = generate_embeddings(
            client,
            texts
        )

        # Save each completed batch immediately
        with OUTPUT_FILE.open(
            "a",
            encoding="utf-8"
        ) as output_file:

            for chunk, vector in zip(batch, vectors):

                record = {
                    **chunk,
                    "embedding_model": MODEL_NAME,
                    "embedding_dimensions": DIMENSIONS,
                    "embedding": vector
                }

                output_file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

        processed += len(batch)

        print(
            f"Processed {processed}/{len(pending_chunks)} "
            f"new chunks"
        )

        # Pause between API requests
        if start + BATCH_SIZE < len(pending_chunks):
            time.sleep(BATCH_DELAY)

    # Final summary
    final_ids = load_completed_ids()

    print("\n========== EMBEDDING SUMMARY ==========")

    print(f"Total source chunks: {len(chunks)}")
    print(f"New embeddings generated: {processed}")
    print(f"Total embeddings available: {len(final_ids)}")
    print(f"Remaining chunks: {len(chunks) - len(final_ids)}")

    print(f"Output file: {OUTPUT_FILE}")

    if len(final_ids) == len(chunks):
        print("\nAll embeddings generated successfully!")
    else:
        print("\nEmbedding process is not yet complete.")


if __name__ == "__main__":
    main()

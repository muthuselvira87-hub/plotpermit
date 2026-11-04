
import json
from pathlib import Path

# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "pdf_pages.jsonl"

OUTPUT_FILE = BASE_DIR / "data" / "processed" / "chunks.jsonl"


# ==========================================
# CHUNKING SETTINGS
# ==========================================

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


# ==========================================
# TEXT CHUNKING FUNCTION
# ==========================================

def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Split text into smaller overlapping chunks."""

    text = text.strip()

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        # Try to end at a natural text boundary.
        if end < text_length:

            search_start = start + int(chunk_size * 0.6)

            boundaries = [
                text.rfind("\n\n", search_start, end),
                text.rfind("\n", search_start, end),
                text.rfind(". ", search_start, end),
                text.rfind(" ", search_start, end)
            ]

            best_boundary = max(boundaries)

            if best_boundary > search_start:
                end = best_boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Move backwards to preserve overlapping context.
        start = max(end - overlap, start + 1)

    return chunks


# ==========================================
# MAIN CHUNKING FUNCTION
# ==========================================

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_pages = 0
    skipped_pages = 0
    total_chunks = 0

    print("Starting document chunking...\n")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as input_file, OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as output_file:

        for line in input_file:

            if not line.strip():
                continue

            page = json.loads(line)
            total_pages += 1

            text = page.get("text", "").strip()

            # Skip blank pages.
            if not text:
                skipped_pages += 1
                continue

            chunks = split_text(text)

            for index, chunk in enumerate(chunks, start=1):

                chunk_record = {
                    "chunk_id": (
                        f"{page['source']}"
                        f"_page_{page['page_number']}"
                        f"_chunk_{index}"
                    ),

                    "source": page["source"],

                    "page_number": page["page_number"],

                    "chunk_index": index,

                    "text": chunk,

                    "character_count": len(chunk)
                }

                output_file.write(
                    json.dumps(
                        chunk_record,
                        ensure_ascii=False
                    ) + "\n"
                )

                total_chunks += 1

    # ======================================
    # CHUNKING SUMMARY
    # ======================================

    print("\n========== CHUNKING SUMMARY ==========")

    print(f"Total pages read: {total_pages}")

    print(f"Blank pages skipped: {skipped_pages}")

    print(f"Total chunks created: {total_chunks}")

    print(f"Chunk size: {CHUNK_SIZE} characters")

    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")

    print(f"Output file: {OUTPUT_FILE}")

    print("\nChunking completed successfully!")


if __name__ == "__main__":
    main()

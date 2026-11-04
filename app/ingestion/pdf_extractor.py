
import json
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader


# ==========================================
# PROJECT DIRECTORIES
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

PDF_DIR = BASE_DIR / "data" / "sample"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "pdf_pages.jsonl"


# ==========================================
# OCR SOFTWARE PATHS
# ==========================================

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\HOME\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ==========================================
# OCR FUNCTION
# ==========================================

def perform_ocr(
    pdf_path: Path,
    page_number: int,
    language: str = "eng+tam"
) -> str:
    """Extract text from a PDF page using OCR."""

    images = convert_from_path(
        str(pdf_path),
        first_page=page_number,
        last_page=page_number,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    if not images:
        return ""

    text = pytesseract.image_to_string(
        images[0],
        lang=language,
        config="--psm 6"
    )

    return text.strip()


# ==========================================
# SELECT OCR LANGUAGE
# ==========================================

def get_ocr_language(
    pdf_path: Path,
    page_number: int
) -> str:
    """Select OCR language for a particular page."""

    # These two pages contain English text.
    if (
        pdf_path.name
        == "TN_Combined_Development_Building_Rules_2019.pdf"
        and page_number in (9, 10)
    ):
        return "eng"

    # Default OCR language.
    return "eng+tam"


# ==========================================
# PDF EXTRACTION FUNCTION
# ==========================================

def extract_pdf(pdf_path: Path) -> list[dict]:
    """Extract text and metadata from every PDF page."""

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        print(f"Processing page: {page_number}")

        # Extract normal PDF text.
        text = page.extract_text(
            extraction_mode="layout"
        ) or ""

        # Count embedded images.
        try:
            image_count = len(page.images)
        except Exception:
            image_count = None

        status = "extracted"
        ocr_used = False
        ocr_language = None

        # Run OCR when extracted text is too short.
        if len(text.strip()) < 30:

            try:
                ocr_language = get_ocr_language(
                    pdf_path,
                    page_number
                )

                ocr_text = perform_ocr(
                    pdf_path,
                    page_number,
                    ocr_language
                )

                # Use OCR when it gives more text.
                if len(ocr_text) > len(text.strip()):

                    text = ocr_text
                    ocr_used = True

                # Determine extraction status.
                if len(text.strip()) >= 30:

                    if ocr_used:
                        status = "ocr_extracted"
                    else:
                        status = "extracted"

                elif image_count and image_count > 0:

                    status = "needs_ocr"

                else:

                    status = "review"

            except Exception as error:

                print(
                    f"OCR failed: {pdf_path.name}, "
                    f"page {page_number}: {error}"
                )

                status = "ocr_failed"

        # Store page-level information.
        pages.append({

            "source": pdf_path.name,

            "page_number": page_number,

            "text": text.strip(),

            "character_count": len(text.strip()),

            "image_count": image_count,

            "ocr_used": ocr_used,

            "ocr_language": (
                ocr_language if ocr_used else None
            ),

            "status": status

        })

    return pages


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    if not PDF_DIR.exists():

        raise FileNotFoundError(
            f"PDF folder not found: {PDF_DIR}"
        )

    pdf_files = sorted(
        PDF_DIR.glob("*.pdf")
    )

    if not pdf_files:

        raise FileNotFoundError(
            f"No PDF files found in {PDF_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    total_pages = 0
    extracted_pages = 0
    ocr_pages = 0
    review_pages = 0
    failed_pages = 0

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as output:

        for pdf_path in pdf_files:

            print("\n================================")
            print(f"Processing PDF: {pdf_path.name}")
            print("================================")

            pages = extract_pdf(pdf_path)

            for page in pages:

                output.write(
                    json.dumps(
                        page,
                        ensure_ascii=False
                    ) + "\n"
                )

                total_pages += 1

                if page["status"] == "extracted":

                    extracted_pages += 1

                elif page["status"] == "ocr_extracted":

                    ocr_pages += 1

                elif page["status"] == "review":

                    review_pages += 1

                elif page["status"] in (
                    "needs_ocr",
                    "ocr_failed"
                ):

                    failed_pages += 1

            print(
                f"Pages processed: {len(pages)}"
            )

    # ======================================
    # EXTRACTION SUMMARY
    # ======================================

    print("\n========== EXTRACTION SUMMARY ==========")

    print(f"Total PDFs: {len(pdf_files)}")

    print(f"Total pages: {total_pages}")

    print(f"Extracted pages: {extracted_pages}")

    print(f"OCR extracted pages: {ocr_pages}")

    print(f"Pages requiring review: {review_pages}")

    print(
        f"OCR failed / still needing OCR: {failed_pages}"
    )

    print(f"Output file: {OUTPUT_FILE}")


# ==========================================
# RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    main()

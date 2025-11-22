# ingestion/parse_pdf.py

from pathlib import Path
from typing import Dict, List

import pdfplumber

from config import PDF_PATH


def extract_pages() -> List[Dict]:
    """
    Extract raw text per page from PDF.
    Returns: [{ 'page_number': int, 'text': str }]
    """
    pdf_file = Path(PDF_PATH)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}")

    pages: List[Dict] = []
    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page_number": i + 1, "text": text})
    return pages


def is_chapter_heading(line: str) -> bool:
    """
    Heuristic for chapter/section titles.
    Adjust if needed based on how the BMW PDF looks.
    """
    s = line.strip()
    if not s:
        return False

    # simple heuristics
    if s.isupper() and 3 <= len(s.split()) <= 8:
        return True
    if s.lower().startswith(("getting in", "on the road", "parking", "mobility")):
        return True

    return False


def parse_pdf_to_chapter_lines() -> List[Dict]:
    """
    Parse PDF into line-level entries with chapter & page.
    Returns: [{ 'page_number', 'chapter', 'text' }]
    """
    pages = extract_pages()
    current_chapter = "UNKNOWN"
    entries: List[Dict] = []

    for p in pages:
        page_no = p["page_number"]
        for line in (p["text"] or "").splitlines():
            if is_chapter_heading(line):
                current_chapter = line.strip()
                continue
            if line.strip():
                entries.append(
                    {
                        "page_number": page_no,
                        "chapter": current_chapter,
                        "text": line.strip(),
                    }
                )
    return entries


if __name__ == "__main__":
    data = parse_pdf_to_chapter_lines()
    print("Sample:", data[:10])

# utils/text_chunker.py

from typing import Dict, List
from uuid import uuid4

from config import CHUNK_SIZE, CHUNK_OVERLAP


def build_chunks(entries: List[Dict]) -> List[Dict]:
    """
    entries: [{ 'page_number', 'chapter', 'text' }]
    returns chunks: [{id, text, chapter, page_number}]
    """
    chunks: List[Dict] = []
    if not entries:
        return chunks

    buffer = ""
    last_chapter = entries[0]["chapter"]
    last_page = entries[0]["page_number"]

    for e in entries:
        text = e["text"]
        chapter = e["chapter"]
        page = e["page_number"]

        # If chapter changes, flush buffer
        if chapter != last_chapter and buffer:
            chunks.append(
                {
                    "id": str(uuid4()),
                    "text": buffer.strip(),
                    "chapter": last_chapter,
                    "page_number": last_page,
                }
            )
            buffer = ""

        # Normal chunk building
        if len(buffer) + len(text) + 1 <= CHUNK_SIZE:
            buffer = (buffer + " " + text).strip()
        else:
            chunks.append(
                {
                    "id": str(uuid4()),
                    "text": buffer.strip(),
                    "chapter": chapter,
                    "page_number": page,
                }
            )
            buffer = (buffer[-CHUNK_OVERLAP:] + " " + text).strip()

        last_chapter = chapter
        last_page = page

    if buffer:
        chunks.append(
            {
                "id": str(uuid4()),
                "text": buffer.strip(),
                "chapter": last_chapter,
                "page_number": last_page,
            }
        )

    return chunks

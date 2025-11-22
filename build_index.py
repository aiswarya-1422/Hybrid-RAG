# ingestion/build_index.py

import time

import chromadb
from chromadb.config import Settings
from tqdm import tqdm

from config import VECTOR_DB_DIR, PDF_PATH
from ingestion.parse_pdf import parse_pdf_to_chapter_lines
from utils.text_chunker import build_chunks
from utils.ollama_client import get_embeddings


def get_collection():
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    return client.get_or_create_collection(name="bmw_x5_manual")


def main():
    print("[INGEST] Parsing PDF...")
    entries = parse_pdf_to_chapter_lines()
    print(f"[INGEST] Line entries: {len(entries)}")

    print("[INGEST] Building chunks...")
    chunks = build_chunks(entries)
    print(f"[INGEST] Chunks: {len(chunks)}")

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [
        {"source": PDF_PATH, "chapter": c["chapter"], "page": c["page_number"]}
        for c in chunks
    ]

    print("[INGEST] Generating embeddings and storing in Chroma...")
    coll = get_collection()

    t0 = time.perf_counter()
    embeddings = get_embeddings(texts)
    embed_time = time.perf_counter() - t0
    print(f"[INGEST] Embedding time: {embed_time:.2f} seconds")

    coll.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    print("[INGEST] Done. Index ready.")


if __name__ == "__main__":
    main()

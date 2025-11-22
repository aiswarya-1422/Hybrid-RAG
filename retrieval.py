# api/retrieval.py

import time
from typing import Dict, List, Optional, Tuple

import chromadb

from config import VECTOR_DB_DIR, TOP_K, MIN_SIMILARITY_THRESHOLD
from utils.ollama_client import generate_answer


def get_collection():
    """
    Connect to the Chroma collection created by ingestion.build_index.
    """
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    return client.get_collection(name="bmw_x5_manual")


def get_all_chapters() -> List[str]:
    """
    Read distinct chapter names from stored metadatas.
    """
    coll = get_collection()
    data = coll.get()
    chapters = {m["chapter"] for m in data["metadatas"]}
    return sorted(list(chapters))


def guess_chapter(question: str, chapters: List[str]) -> Optional[str]:
    """
    Simple heuristic to guess relevant chapter from query text.
    """
    q = question.lower()
    best = None
    best_len = 0

    for ch in chapters:
        for token in ch.lower().split():
            if token and token in q and len(token) > best_len:
                best = ch
                best_len = len(token)

    return best


def retrieve_chunks(question: str) -> Tuple[List[Dict], float, Optional[str]]:
    """
    Hybrid retrieval: chapter metadata filter + vector search.
    """
    coll = get_collection()
    chapters = get_all_chapters()
    chapter = guess_chapter(question, chapters)

    where = {"chapter": chapter} if chapter else None

    t0 = time.perf_counter()
    result = coll.query(query_texts=[question], n_results=TOP_K, where=where)
    retrieval_ms = (time.perf_counter() - t0) * 1000.0

    docs = result["documents"][0]
    metas = result["metadatas"][0]
    distances = result.get("distances", [[0.0] * len(docs)])[0]

    chunks: List[Dict] = []
    for d, m, dist in zip(docs, metas, distances):
        score = 1.0 / (1.0 + dist)  # simple dist→similarity
        chunks.append(
            {
                "text": d,
                "chapter": m["chapter"],
                "page": m["page"],
                "score": score,
            }
        )

    return chunks, retrieval_ms, chapter


def build_prompt(question: str, chunks: List[Dict]) -> str:
    ctx = ""
    for i, c in enumerate(chunks, start=1):
        ctx += (
            f"[Chunk {i} | Chapter: {c['chapter']} | Page: {c['page']}]\n"
            f"{c['text']}\n\n"
        )

    prompt = f"""
You are a support assistant for a BMW X5 Owner's Manual.
Answer strictly based on the context below.
If the answer is not clearly contained in the context, reply exactly:
"I don't know based on the manual."

Context:
{ctx}

Question:
{question}

Answer:
""".strip()

    return prompt


def answer_query(question: str) -> Dict:
    """
    Main RAG pipeline.
    """
    chunks, retrieval_ms, chapter = retrieve_chunks(question)

    if not chunks or max(c["score"] for c in chunks) < MIN_SIMILARITY_THRESHOLD:
        return {
            "answer": "I don't know based on the manual.",
            "sources": chunks,
            "retrieval_latency_ms": retrieval_ms,
            "generation_latency_ms": 0.0,
            "applied_chapter_filter": chapter,
        }

    prompt = build_prompt(question, chunks)

    t0 = time.perf_counter()
    answer = generate_answer(prompt)
    gen_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_latency_ms": retrieval_ms,
        "generation_latency_ms": gen_ms,
        "applied_chapter_filter": chapter,
    }

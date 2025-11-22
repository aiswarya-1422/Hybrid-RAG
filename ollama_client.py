# utils/ollama_client.py

from typing import List
import httpx

from config import OLLAMA_BASE_URL, EMBED_MODEL, LLM_MODEL


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Ollama's embedding model.
    """
    embeddings: List[List[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for t in texts:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": t},
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings.append(data["embedding"])
    return embeddings


def generate_answer(prompt: str) -> str:
    """
    Call Ollama LLM (llama3) to generate an answer from a prompt.
    """
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["response"].strip()

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.loader import load_documents


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def chunk_text(text: str, chunk_size: int = 700) -> list[str]:
    """
    Split a policy document into small overlapping chunks.
    """
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0
    overlap = 100

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def build_chunks() -> list[dict[str, str]]:
    """
    Load all policies and split them into retrievable chunks.
    """
    chunks = []

    for document in load_documents():
        for chunk in chunk_text(document["text"]):
            chunks.append(
                {
                    "source": document["source"],
                    "text": chunk,
                }
            )

    return chunks


def get_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def load_embeddings() -> tuple[np.ndarray, list[dict[str, str]]]:
    """
    Load locally stored policy embeddings and metadata.
    """
    embeddings_path = EMBEDDINGS_DIR / "policy_embeddings.npy"
    metadata_path = EMBEDDINGS_DIR / "policy_chunks.json"

    if not embeddings_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Policy embeddings not found. Run the embedding generation script first."
        )

    embeddings = np.load(embeddings_path)

    chunks = json.loads(
        metadata_path.read_text(encoding="utf-8")
    )

    return embeddings, chunks


def retrieve(
    query: str,
    top_k: int = 3,
) -> list[dict[str, str]]:
    """
    Retrieve the most semantically relevant policy chunks.
    """
    embeddings, chunks = load_embeddings()

    model = get_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    )[0]

    scores = embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in top_indices:
        results.append(
            {
                "source": chunks[index]["source"],
                "text": chunks[index]["text"],
                "score": float(scores[index]),
            }
        )

    return results
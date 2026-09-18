from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.retriever import build_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def create_embeddings() -> tuple[np.ndarray, list[dict[str, str]]]:
    """
    Create embeddings for all knowledge-base chunks.
    """
    chunks = build_chunks()

    texts = [chunk["text"] for chunk in chunks]

    model = get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return np.asarray(embeddings), chunks


def save_embeddings() -> None:
    """
    Generate and save embeddings and their metadata locally.
    """
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    embeddings, chunks = create_embeddings()

    np.save(
        EMBEDDINGS_DIR / "policy_embeddings.npy",
        embeddings,
    )

    metadata_path = EMBEDDINGS_DIR / "policy_chunks.json"

    import json

    metadata_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved {len(chunks)} chunks.")
    print(f"Embeddings shape: {embeddings.shape}")
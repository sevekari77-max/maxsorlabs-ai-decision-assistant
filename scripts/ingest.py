import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.embedder import save_embeddings


if __name__ == "__main__":
    print("Starting policy ingestion...")
    print(f"Knowledge base: {PROJECT_ROOT / 'candidate_pack' / 'knowledge_base'}")
    print()

    save_embeddings()

    print()
    print("Policy ingestion completed successfully.")
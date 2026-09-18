from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "candidate_pack" / "knowledge_base"


def load_documents() -> list[dict[str, str]]:
    """
    Load all Markdown policy documents from the knowledge base.
    """
    documents = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(
            {
                "source": file_path.name,
                "text": text,
            }
        )

    return documents
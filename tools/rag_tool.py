import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag import ask_question


def search_knowledge_base(question: str):
    """Search the HR knowledge base and return a grounded answer with sources."""
    result = ask_question(question)

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"]
    }
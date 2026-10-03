import json
from pathlib import Path

import faiss
import numpy as np
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT_DIR / "data" / "knowledge_base"
INDEX_DIR = ROOT_DIR / "data" / "knowledge_base_index"

OLLAMA_HOST = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["embedding"]


def chunk_text(text):
    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_DIR.rglob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            documents.append({
                "source": str(file_path.relative_to(ROOT_DIR)),
                "chunk_id": index,
                "text": chunk
            })

    return documents


def main():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    documents = load_documents()

    if not documents:
        print("No knowledge-base documents found.")
        return

    print(f"Found {len(documents)} document chunks.")

    embeddings = []

    for index, document in enumerate(documents, start=1):
        print(f"Embedding chunk {index}/{len(documents)}")
        embeddings.append(get_embedding(document["text"]))

    embedding_matrix = np.array(embeddings, dtype="float32")

    faiss.normalize_L2(embedding_matrix)

    dimension = embedding_matrix.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_matrix)

    faiss.write_index(
        index,
        str(INDEX_DIR / "knowledge_base.faiss")
    )

    with open(INDEX_DIR / "metadata.json", "w", encoding="utf-8") as file:
        json.dump(
            documents,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("RAG INDEX CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Documents/chunks: {len(documents)}")
    print(f"Embedding dimension: {dimension}")
    print(f"Index: {INDEX_DIR / 'knowledge_base.faiss'}")
    print(f"Metadata: {INDEX_DIR / 'metadata.json'}")


if __name__ == "__main__":
    main()
import json
from pathlib import Path

import faiss
import numpy as np
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = ROOT_DIR / "data" / "knowledge_base_index"

OLLAMA_HOST = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


class RAGRetriever:
    def __init__(self, top_k=4):
        self.top_k = top_k
        self.index_path = INDEX_DIR / "knowledge_base.faiss"
        self.metadata_path = INDEX_DIR / "metadata.json"

        if not self.index_path.exists():
            raise FileNotFoundError(
                "FAISS index not found. Run python .\\rag\\build_index.py first."
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                "RAG metadata not found. Run python .\\rag\\build_index.py first."
            )

        self.index = faiss.read_index(str(self.index_path))

        with open(self.metadata_path, "r", encoding="utf-8") as file:
            self.metadata = json.load(file)

    def get_embedding(self, text):
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

    def search(self, query):
        embedding = np.array(
            [self.get_embedding(query)],
            dtype="float32"
        )

        faiss.normalize_L2(embedding)

        scores, indices = self.index.search(
            embedding,
            min(self.top_k, len(self.metadata))
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            document = self.metadata[index]

            results.append({
                "score": float(score),
                "source": document["source"],
                "chunk_id": document["chunk_id"],
                "text": document["text"]
            })

        return results
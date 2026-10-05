import json
import os

import faiss
import numpy as np
import ollama

from dotenv import load_dotenv

try:
    from .reranker import Reranker
except ImportError:
    from reranker import Reranker


load_dotenv()


INDEX_FILE = "data/faiss.index"
METADATA_FILE = "data/index_metadata.json"

MODEL_NAME = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text"
)


reranker = Reranker()


def load_search_data():
    print("Loading FAISS index...")

    index = faiss.read_index(INDEX_FILE)

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    metadata_by_id = {
        item["vector_id"]: item
        for item in metadata
    }

    return index, metadata_by_id


def embed_query(query):
    response = ollama.embed(
        model=MODEL_NAME,
        input=query
    )

    vector = np.array(
        [response["embeddings"][0]],
        dtype="float32"
    )

    faiss.normalize_L2(vector)

    return vector


def semantic_search(
    query,
    user_id=None,
    candidate_k=20,
    category_filter=None
):
    index, metadata_by_id = load_search_data()

    query_vector = embed_query(query)

    scores, vector_ids = index.search(
        query_vector,
        candidate_k
    )

    candidates = []

    for score, vector_id in zip(
        scores[0],
        vector_ids[0]
    ):
        if vector_id == -1:
            continue

        vector_id = int(vector_id)

        if vector_id not in metadata_by_id:
            continue

        result = metadata_by_id[vector_id].copy()

        if category_filter is not None:
            if result["category"].lower() != category_filter.lower():
                continue

        result["similarity"] = float(score)

        candidates.append(result)

    return candidates


def improved_search(
    query,
    user_id=None,
    top_k=5,
    category_filter=None
):
    print("\nRunning semantic search...")

    candidates = semantic_search(
        query=query,
        user_id=user_id,
        candidate_k=20,
        category_filter=category_filter
    )

    print(
        "Candidates retrieved:",
        len(candidates)
    )

    results = reranker.rerank(
        query=query,
        results=candidates,
        top_k=top_k
    )

    return results
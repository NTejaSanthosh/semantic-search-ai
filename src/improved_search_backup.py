import json
import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types
from reranker import Reranker

INDEX_FILE = "data/faiss.index"
METADATA_FILE = "data/index_metadata.json"
MODEL_NAME = "gemini-embedding-001"

load_dotenv()

api_key = __import__("os").getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)

reranker = Reranker()


def load_search_data():

    print("Loading FAISS index...")

    index = faiss.read_index(INDEX_FILE)

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    metadata_by_id = {
        item["vector_id"]: item
        for item in metadata
    }

    return index, metadata_by_id


def embed_query(query):

    result = client.models.embed_content(
        model=MODEL_NAME,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )

    vector = np.array(
        [result.embeddings[0].values],
        dtype="float32"
    )

    faiss.normalize_L2(vector)

    return vector


def semantic_search(
    query,
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

            if (
                result["category"].lower()
                != category_filter.lower()
            ):
                continue

        result["similarity"] = float(score)

        candidates.append(result)

    return candidates


def improved_search(
    query,
    top_k=5,
    category_filter=None
):

    print("\nRunning improved semantic search...")

    candidates = semantic_search(
        query=query,
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


def main():

    print("=" * 70)
    print("IMPROVED SEMANTIC SEARCH")
    print("=" * 70)

    query = input(
        "\nEnter your question: "
    )

    category = input(
        "Enter category filter (press Enter to skip): "
    ).strip()

    if category == "":
        category = None

    results = improved_search(
        query=query,
        top_k=5,
        category_filter=category
    )

    print("\n" + "=" * 70)
    print("FINAL RERANKED RESULTS")
    print("=" * 70)

    for rank, result in enumerate(
        results,
        start=1
    ):

        print()
        print(f"Rank: {rank}")
        print(f"Document ID: {result['doc_id']}")
        print(f"Title: {result['title']}")
        print(f"Category: {result['category']}")
        print(
            f"Vector similarity: "
            f"{result['similarity']:.4f}"
        )
        print(
            f"Rerank score: "
            f"{result['rerank_score']:.4f}"
        )

        print("\nText:")
        print(result["text"][:500])

        print("-" * 70)


if __name__ == "__main__":
    main()
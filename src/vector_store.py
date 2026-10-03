import json
import os
import faiss
import numpy as np

INPUT_FILE = "data/embeddings.json"
INDEX_FILE = "data/faiss.index"
METADATA_FILE = "data/index_metadata.json"


def build_index():
    print("Loading embeddings...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        embedded_chunks = json.load(file)

    print("Total embeddings:", len(embedded_chunks))

    vectors = np.array(
        [item["embedding"] for item in embedded_chunks],
        dtype="float32"
    )

    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]

    print("Vector shape:", vectors.shape)
    print("Creating FAISS index...")

    base_index = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIDMap2(base_index)

    ids = np.arange(
        1,
        len(embedded_chunks) + 1,
        dtype="int64"
    )

    index.add_with_ids(vectors, ids)

    print("FAISS index created!")
    print("Number of vectors:", index.ntotal)
    print("Vector dimension:", dimension)

    os.makedirs("data", exist_ok=True)

    faiss.write_index(index, INDEX_FILE)

    metadata = []

    for item, vector_id in zip(embedded_chunks, ids):
        metadata.append({
            "vector_id": int(vector_id),
            "doc_id": item["doc_id"],
            "title": item["title"],
            "category": item["category"],
            "source": item["source"],
            "chunk_number": item["chunk_number"],
            "text": item["text"]
        })

    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("FAISS index saved successfully!")
    print("Index file:", INDEX_FILE)
    print("Metadata file:", METADATA_FILE)


if __name__ == "__main__":
    build_index()
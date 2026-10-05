import os
import json

import faiss
import numpy as np
import ollama

from dotenv import load_dotenv


INPUT_FILE = "data/chunks.json"
OUTPUT_FILE = "data/embeddings.json"

load_dotenv()

MODEL_NAME = os.getenv(
    "OLLAMA_EMBEDDING_MODEL",
    "nomic-embed-text"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

os.environ["OLLAMA_HOST"] = OLLAMA_HOST


def generate_embeddings():
    print("Loading chunks...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    print("Total chunks:", len(chunks))
    print("Embedding model:", MODEL_NAME)
    print("Generating Ollama embeddings...")

    embedded_chunks = []

    for index, chunk in enumerate(chunks):
        print(
            f"Embedding {index + 1}/{len(chunks)}"
        )

        response = ollama.embed(
            model=MODEL_NAME,
            input=chunk["text"]
        )

        embedding = response["embeddings"][0]

        embedded_chunk = {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "category": chunk["category"],
            "source": chunk["source"],
            "chunk_number": chunk["chunk_number"],
            "text": chunk["text"],
            "embedding": embedding
        }

        embedded_chunks.append(
            embedded_chunk
        )

    print()
    print("Saving embeddings...")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            embedded_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Embedding generation completed!")
    print(
        "Total embedded chunks:",
        len(embedded_chunks)
    )
    print(
        "Embedding dimensions:",
        len(embedded_chunks[0]["embedding"])
    )
    print(
        "Saved to:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    generate_embeddings()
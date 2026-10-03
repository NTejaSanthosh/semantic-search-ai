import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


INPUT_FILE = "data/chunks.json"
OUTPUT_FILE = "data/embeddings.json"

MODEL_NAME = "gemini-embedding-001"


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)


def generate_embeddings():

    print("Loading chunks...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print("Total chunks:", len(chunks))
    print("Generating Gemini embeddings...")

    embedded_chunks = []

    for index, chunk in enumerate(chunks):

        print(f"Embedding {index + 1}/{len(chunks)}")

        result = client.models.embed_content(
            model=MODEL_NAME,
            contents=chunk["text"],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )

        embedding = result.embeddings[0].values

        embedded_chunk = {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "category": chunk["category"],
            "source": chunk["source"],
            "chunk_number": chunk["chunk_number"],
            "text": chunk["text"],
            "embedding": embedding
        }

        embedded_chunks.append(embedded_chunk)

        time.sleep(0.2)

    print()
    print("Saving embeddings...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            embedded_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Embedding generation completed!")
    print("Total embedded chunks:", len(embedded_chunks))
    print("Embedding dimensions:", len(embedded_chunks[0]["embedding"]))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_embeddings()
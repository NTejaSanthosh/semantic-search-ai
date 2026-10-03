import json
import os


INPUT_FILE = "data/documents.json"
OUTPUT_FILE = "data/chunks.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def create_chunks(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0
    chunk_number = 0

    while start < len(text):

        end = start + chunk_size

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "chunk_number": chunk_number,
                "text": chunk_text
            })

        chunk_number += 1

        start = end - overlap

    return chunks


def main():

    print("Loading documents...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    all_chunks = []

    print("Creating chunks...")

    for document in documents:

        chunks = create_chunks(
            document["text"],
            CHUNK_SIZE,
            CHUNK_OVERLAP
        )

        for chunk in chunks:

            chunk_record = {
                "doc_id": document["doc_id"],
                "title": document["title"],
                "category": document["category"],
                "source": document["source"],
                "chunk_number": chunk["chunk_number"],
                "text": chunk["text"]
            }

            all_chunks.append(chunk_record)

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            all_chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Chunking completed!")
    print("Documents:", len(documents))
    print("Total chunks:", len(all_chunks))
    print("Chunk size:", CHUNK_SIZE)
    print("Chunk overlap:", CHUNK_OVERLAP)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
import json
import os
import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

INDEX_FILE = "data/faiss.index"
METADATA_FILE = "data/index_metadata.json"
MODEL_NAME = "gemini-embedding-001"

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

client = genai.Client(api_key=api_key)


def load_data():
    index = faiss.read_index(INDEX_FILE)

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return index, metadata


def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )


def generate_embedding(text):
    result = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )

    vector = np.array(
        [result.embeddings[0].values],
        dtype="float32"
    )

    faiss.normalize_L2(vector)

    return vector


def get_next_vector_id(metadata):
    if not metadata:
        return 1

    return max(
        item["vector_id"]
        for item in metadata
    ) + 1


def add_document(
    doc_id,
    title,
    category,
    source,
    text,
    date=None,
    version=None
):
    index, metadata = load_data()

    for item in metadata:
        if item["doc_id"] == doc_id:
            print("Document already exists:", doc_id)
            return

    print("Generating embedding...")

    vector = generate_embedding(text)

    vector_id = get_next_vector_id(metadata)

    index.add_with_ids(
        vector,
        np.array([vector_id], dtype="int64")
    )

    metadata.append({
        "vector_id": vector_id,
        "doc_id": doc_id,
        "title": title,
        "category": category,
        "source": source,
        "chunk_number": 0,
        "text": text,
        "date": date,
        "version": version
    })

    faiss.write_index(index, INDEX_FILE)

    save_metadata(metadata)

    print()
    print("Document added successfully!")
    print("Document ID:", doc_id)
    print("Vector ID:", vector_id)
    print("Date:", date)
    print("Version:", version)
    print("Total vectors:", index.ntotal)


def update_document(
    doc_id,
    title,
    category,
    source,
    text,
    date=None,
    version=None
):
    index, metadata = load_data()

    document = None

    for item in metadata:
        if item["doc_id"] == doc_id:
            document = item
            break

    if document is None:
        print("Document not found:", doc_id)
        return

    print("Generating new embedding...")

    new_vector = generate_embedding(text)

    vector_id = document["vector_id"]

    index.remove_ids(
        np.array([vector_id], dtype="int64")
    )

    index.add_with_ids(
        new_vector,
        np.array([vector_id], dtype="int64")
    )

    document["title"] = title
    document["category"] = category
    document["source"] = source
    document["text"] = text
    document["date"] = date
    document["version"] = version

    faiss.write_index(index, INDEX_FILE)

    save_metadata(metadata)

    print()
    print("Document updated successfully!")
    print("Document ID:", doc_id)
    print("Vector ID:", vector_id)
    print("Date:", date)
    print("Version:", version)
    print("Total vectors:", index.ntotal)


def delete_document(doc_id):
    index, metadata = load_data()

    document = None

    for item in metadata:
        if item["doc_id"] == doc_id:
            document = item
            break

    if document is None:
        print("Document not found:", doc_id)
        return

    vector_id = document["vector_id"]

    print("Deleting document:", doc_id)

    index.remove_ids(
        np.array([vector_id], dtype="int64")
    )

    metadata = [
        item
        for item in metadata
        if item["doc_id"] != doc_id
    ]

    faiss.write_index(index, INDEX_FILE)

    save_metadata(metadata)

    print()
    print("Document deleted successfully!")
    print("Deleted ID:", doc_id)
    print("Vector ID:", vector_id)
    print("Total vectors:", index.ntotal)


def show_document_count():
    index, metadata = load_data()

    print()
    print("Current knowledge base")
    print("----------------------")
    print("Metadata records:", len(metadata))
    print("FAISS vectors:", index.ntotal)


if __name__ == "__main__":
    show_document_count()
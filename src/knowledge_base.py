import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCUMENTS_FILE = os.path.join(BASE_DIR, "data", "documents.json")
CHUNKS_FILE = os.path.join(BASE_DIR, "data", "chunks.json")


def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        raise FileNotFoundError(
            f"Knowledge Base documents file not found: {DOCUMENTS_FILE}"
        )

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_chunks():
    if not os.path.exists(CHUNKS_FILE):
        raise FileNotFoundError(
            f"Knowledge Base chunks file not found: {CHUNKS_FILE}"
        )

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def list_documents(query=None, category=None):
    documents = load_documents()
    chunks = load_chunks()

    if query:
        query = query.strip().lower()

        documents = [
            document
            for document in documents
            if query in str(document.get("doc_id", "")).lower()
            or query in str(document.get("title", "")).lower()
            or query in str(document.get("category", "")).lower()
            or query in str(document.get("source", "")).lower()
            or query in str(document.get("text", "")).lower()
        ]

    if category:
        category = category.strip().lower()

        documents = [
            document
            for document in documents
            if str(document.get("category", "")).lower() == category
        ]

    chunk_counts = {}

    for chunk in chunks:
        doc_id = chunk.get("doc_id")

        if doc_id:
            chunk_counts[doc_id] = chunk_counts.get(doc_id, 0) + 1

    results = []

    for document in documents:
        doc_id = document.get("doc_id")

        results.append(
            {
                "doc_id": doc_id,
                "title": document.get("title"),
                "category": document.get("category"),
                "source": document.get("source"),
                "date": document.get("date"),
                "version": document.get("version"),
                "chunk_count": chunk_counts.get(doc_id, 0),
            }
        )

    return results


def get_document(doc_id):
    documents = load_documents()

    for document in documents:
        if document.get("doc_id") == doc_id:
            return document

    return None


def get_document_chunks(doc_id):
    chunks = load_chunks()

    return [
        chunk
        for chunk in chunks
        if chunk.get("doc_id") == doc_id
    ]


def get_categories():
    documents = load_documents()

    categories = sorted(
        {
            str(document.get("category"))
            for document in documents
            if document.get("category")
        }
    )

    return categories
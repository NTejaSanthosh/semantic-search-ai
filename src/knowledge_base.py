
import json
import os

from .permissions import (
    can_access_document,
    filter_accessible_documents,
)

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


def list_documents(query=None, category=None, user_id=None):
    documents = load_documents()
    documents = filter_accessible_documents(documents, user_id)

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

    accessible_ids = {
        document.get("doc_id")
        for document in documents
    }

    chunk_counts = {}

    for chunk in load_chunks():
        doc_id = chunk.get("doc_id")

        if doc_id in accessible_ids:
            chunk_counts[doc_id] = chunk_counts.get(doc_id, 0) + 1

    return [
        {
            "doc_id": document.get("doc_id"),
            "title": document.get("title"),
            "category": document.get("category"),
            "source": document.get("source"),
            "date": document.get("date"),
            "version": document.get("version"),
            "chunk_count": chunk_counts.get(document.get("doc_id"), 0),
        }
        for document in documents
    ]


def get_document(doc_id, user_id=None):
    document = next(
        (
            item
            for item in load_documents()
            if item.get("doc_id") == doc_id
        ),
        None,
    )

    if document is None:
        return None

    if not can_access_document(doc_id, user_id):
        return None

    return document


def get_document_chunks(doc_id, user_id=None):
    if not can_access_document(doc_id, user_id):
        return []

    document = get_document(doc_id, user_id)

    if document is None:
        return []

    return [
        chunk
        for chunk in load_chunks()
        if chunk.get("doc_id") == doc_id
    ]


def get_categories(user_id=None):
    documents = filter_accessible_documents(load_documents(), user_id)

    return sorted({
        str(document.get("category"))
        for document in documents
        if document.get("category")
    })

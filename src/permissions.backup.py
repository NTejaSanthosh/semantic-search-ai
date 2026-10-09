
import sqlite3

from .auth import get_connection


def initialize_permissions_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_ownership (
                doc_id TEXT PRIMARY KEY,
                owner_user_id TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def set_document_owner(doc_id, owner_user_id):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO document_ownership (doc_id, owner_user_id)
            VALUES (?, ?)
            ON CONFLICT(doc_id) DO UPDATE SET
                owner_user_id = excluded.owner_user_id
            """,
            (doc_id, owner_user_id),
        )


def can_access_document(doc_id, user_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT owner_user_id
            FROM document_ownership
            WHERE doc_id = ?
            """,
            (doc_id,),
        ).fetchone()

    if row is None:
        return True

    owner_user_id = row["owner_user_id"]

    return owner_user_id is None or owner_user_id == user_id


def filter_accessible_documents(documents, user_id):
    doc_ids = {
        str(document.get("doc_id"))
        for document in documents
        if document.get("doc_id")
    }

    if not doc_ids:
        return []

    placeholders = ",".join("?" for _ in doc_ids)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT doc_id, owner_user_id
            FROM document_ownership
            WHERE doc_id IN ({placeholders})
            """,
            tuple(doc_ids),
        ).fetchall()

    ownership = {
        row["doc_id"]: row["owner_user_id"]
        for row in rows
    }

    return [
        document
        for document in documents
        if (
            document.get("doc_id") not in ownership
            or ownership[document.get("doc_id")] is None
            or ownership[document.get("doc_id")] == user_id
        )
    ]

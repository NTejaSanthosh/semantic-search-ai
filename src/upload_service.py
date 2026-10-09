import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import faiss
import numpy as np
import ollama
from dotenv import load_dotenv

from .permissions import set_document_owner

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = DATA_DIR / "faiss.index"
METADATA_FILE = DATA_DIR / "index_metadata.json"
DOCUMENTS_FILE = DATA_DIR / "documents.json"
CHUNKS_FILE = DATA_DIR / "chunks.json"

MODEL_NAME = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_HOST

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
MAX_CHUNKS_PER_UPLOAD = 500
_index_lock = threading.Lock()


def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_atomic(path, value):
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(value, file, indent=2, ensure_ascii=False)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary_path, path)


def split_text(text):
    text = re.sub(r"\r\n?", "\n", text).strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        if end < len(text):
            boundary = max(
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            )
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    if len(chunks) > MAX_CHUNKS_PER_UPLOAD:
        raise ValueError(
            f"This document is too large to index. "
            f"Limit: {MAX_CHUNKS_PER_UPLOAD} chunks."
        )

    return chunks


def generate_embeddings(text_chunks):
    client = ollama.Client(host=OLLAMA_HOST)
    vectors = []

    for chunk in text_chunks:
        response = client.embed(
            model=MODEL_NAME,
            input=chunk,
        )
        embeddings = response.get("embeddings", [])
        if not embeddings or not embeddings[0]:
            raise RuntimeError("Ollama returned an empty embedding.")

        vector = np.asarray(embeddings[0], dtype="float32")
        vectors.append(vector)

    matrix = np.vstack(vectors).astype("float32")
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise RuntimeError("The generated embeddings are invalid.")

    faiss.normalize_L2(matrix)
    return matrix


def add_uploaded_document(
    title,
    category,
    text,
    owner_user_id,
):
    title = Path(title).name.strip()
    category = (category or "My Uploads").strip()[:100] or "My Uploads"
    text = text.strip()

    if not title or not text:
        raise ValueError("The document title and extracted text are required.")

    text_chunks = split_text(text)
    if not text_chunks:
        raise ValueError("No readable text was found in the uploaded file.")

    embeddings = generate_embeddings(text_chunks)
    doc_id = f"UPLOAD_{uuid.uuid4().hex}"
    source = title
    uploaded_at = datetime.now(timezone.utc).isoformat()

    with _index_lock:
        index = faiss.read_index(str(INDEX_FILE))
        metadata = read_json(METADATA_FILE)
        documents = read_json(DOCUMENTS_FILE)
        all_chunks = read_json(CHUNKS_FILE)

        if not isinstance(index, faiss.IndexIDMap2):
            raise RuntimeError("The existing FAISS index type is not supported.")
        if index.d != embeddings.shape[1]:
            raise RuntimeError(
                f"Embedding dimension mismatch: index={index.d}, "
                f"new={embeddings.shape[1]}."
            )
        if index.ntotal != len(metadata):
            raise RuntimeError(
                "FAISS and metadata counts do not match. "
                "No changes were made."
            )

        existing_ids = {int(item["vector_id"]) for item in metadata}
        if len(existing_ids) != len(metadata):
            raise RuntimeError("Duplicate vector IDs exist in metadata.")

        first_vector_id = max(existing_ids, default=0) + 1
        vector_ids = np.arange(
            first_vector_id,
            first_vector_id + len(text_chunks),
            dtype="int64",
        )

        new_metadata = [
            {
                "vector_id": int(vector_id),
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "source": source,
                "chunk_number": chunk_number,
                "text": chunk,
                "date": uploaded_at,
                "version": "1",
            }
            for chunk_number, (vector_id, chunk) in enumerate(
                zip(vector_ids, text_chunks)
            )
        ]

        document_record = {
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "source": source,
            "text": text,
            "date": uploaded_at,
            "version": "1",
        }

        chunk_records = [
            {
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "source": source,
                "chunk_number": chunk_number,
                "text": chunk,
            }
            for chunk_number, chunk in enumerate(text_chunks)
        ]

        original_index = faiss.serialize_index(index).tobytes()
        original_metadata = json.dumps(
            metadata, ensure_ascii=False
        ).encode("utf-8")
        original_documents = json.dumps(
            documents, ensure_ascii=False
        ).encode("utf-8")
        original_chunks = json.dumps(
            all_chunks, ensure_ascii=False
        ).encode("utf-8")

        try:
            index.add_with_ids(embeddings, vector_ids)
            metadata.extend(new_metadata)
            documents.append(document_record)
            all_chunks.extend(chunk_records)

            set_document_owner(doc_id, owner_user_id)

            faiss.write_index(index, str(INDEX_FILE))
            write_json_atomic(METADATA_FILE, metadata)
            write_json_atomic(DOCUMENTS_FILE, documents)
            write_json_atomic(CHUNKS_FILE, all_chunks)

        except Exception:
            faiss.write_index(
                faiss.deserialize_index(
                    np.frombuffer(original_index, dtype=np.uint8)
                ),
                str(INDEX_FILE),
            )
            METADATA_FILE.write_bytes(original_metadata)
            DOCUMENTS_FILE.write_bytes(original_documents)
            CHUNKS_FILE.write_bytes(original_chunks)
            raise

    return {
        "doc_id": doc_id,
        "title": title,
        "category": category,
        "source": source,
        "chunk_count": len(text_chunks),
        "message": "Document uploaded and indexed successfully.",
    }
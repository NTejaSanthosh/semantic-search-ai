
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    initialize_auth_database,
    validate_auth_configuration,
)
from .rag import ask_question
from .knowledge_base import (
    list_documents,
    get_document,
    get_document_chunks,
    get_categories,
)
from .permissions import initialize_permissions_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_auth_configuration()
    initialize_auth_database()
    initialize_permissions_database()
    yield


app = FastAPI(
    title="Semantic Search AI API",
    version="1.2.0",
    lifespan=lifespan,
)

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://semantic-search-ai-1.onrender.com",
]

frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
allowed_origins = default_origins.copy()

if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

extra_origins = os.getenv("ALLOWED_ORIGINS", "").strip()

if extra_origins:
    for origin in extra_origins.split(","):
        origin = origin.strip().rstrip("/")
        if origin and origin not in allowed_origins:
            allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    category_filter: str | None = None


@app.get("/")
def root():
    return {
        "name": "Semantic Search AI API",
        "status": "online",
        "version": "1.2.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/auth/register", status_code=201)
def register(request: RegisterRequest):
    user = create_user(request.email, request.password)
    token = create_access_token(user)

    return {
        "message": "Account created successfully.",
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    token = create_access_token(user)

    return {
        "message": "Login successful.",
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/auth/me")
def current_user(user=Depends(get_current_user)):
    return {"user": user}


@app.post("/ask")
def ask(
    request: AskRequest,
    user=Depends(get_current_user),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = ask_question(
            question=question,
            user_id=user["user_id"],
            top_k=request.top_k,
            category_filter=request.category_filter,
        )

        normalized_sources = []

        for item in result.get("results", []):
            normalized_sources.append({
                "doc_id": item.get("doc_id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "source": item.get("source"),
                "text": item.get("text"),
                "similarity": item.get("similarity", 0.0),
                "rerank_score": item.get("rerank_score", 0.0),
                "combined_score": item.get("combined_score", 0.0),
                "chunk_number": item.get("chunk_number"),
                "date": item.get("date"),
                "version": item.get("version"),
            })

        return {
            "question": result.get("question"),
            "answer": result.get("answer"),
            "sources": normalized_sources,
            "source_ids": result.get("sources", []),
            "count": len(normalized_sources),
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question.",
        )


@app.get("/documents")
def documents(
    query: str | None = None,
    category: str | None = None,
    user=Depends(get_current_user),
):
    try:
        results = list_documents(
            query=query,
            category=category,
            user_id=user["user_id"],
        )

        return {
            "count": len(results),
            "documents": results,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve documents.",
        )


@app.get("/documents/categories")
def document_categories(user=Depends(get_current_user)):
    try:
        return {
            "categories": get_categories(user["user_id"]),
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve document categories.",
        )


@app.get("/documents/{doc_id}")
def document_details(
    doc_id: str,
    user=Depends(get_current_user),
):
    try:
        document = get_document(
            doc_id,
            user["user_id"],
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return document

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve document details.",
        )


@app.get("/documents/{doc_id}/chunks")
def document_chunks(
    doc_id: str,
    user=Depends(get_current_user),
):
    try:
        document = get_document(
            doc_id,
            user["user_id"],
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        chunks = get_document_chunks(
            doc_id,
            user["user_id"],
        )

        return {
            "doc_id": doc_id,
            "count": len(chunks),
            "chunks": chunks,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve document chunks.",
        )

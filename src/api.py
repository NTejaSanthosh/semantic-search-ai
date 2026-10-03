import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import ask_question


app = FastAPI(
    title="Semantic Search AI API",
    version="1.0.0"
)


default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://semantic-search-ai-1.onrender.com"
]

frontend_url = os.getenv(
    "FRONTEND_URL",
    ""
).strip().rstrip("/")

allowed_origins = default_origins.copy()

if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

extra_origins = os.getenv(
    "ALLOWED_ORIGINS",
    ""
).strip()

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
    allow_headers=["Content-Type", "Accept"]
)


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    category_filter: str | None = None


@app.get("/")
def root():
    return {
        "name": "Semantic Search AI API",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask(request: AskRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = ask_question(
            question=question,
            top_k=request.top_k,
            category_filter=request.category_filter
        )

        normalized_sources = []

        for item in result.get("results", []):

            normalized_sources.append({
                "doc_id": item.get("doc_id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "source": item.get("source"),
                "text": item.get("text"),
                "similarity": item.get(
                    "similarity",
                    0.0
                ),
                "date": item.get("date"),
                "version": item.get("version")
            })

        return {
            "question": result.get("question"),
            "answer": result.get("answer"),
            "sources": normalized_sources,
            "source_ids": result.get(
                "sources",
                []
            ),
            "count": len(normalized_sources)
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
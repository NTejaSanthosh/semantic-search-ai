from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import ask_question

app = FastAPI(
    title="Semantic Search AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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
            normalized_sources.append(
                {
                    "doc_id": item.get("doc_id"),
                    "title": item.get("title"),
                    "category": item.get("category"),
                    "source": item.get("source"),
                    "text": item.get("text"),
                    "similarity": item.get(
                        "similarity",
                        0.0
                    ),
                    "rerank_score": item.get(
                        "rerank_score",
                        0.0
                    ),
                    "date": item.get("date"),
                    "version": item.get("version")
                }
            )

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
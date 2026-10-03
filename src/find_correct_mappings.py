import json
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_FILE = ROOT / "data" / "documents.json"
QUESTIONS_FILE = ROOT / "data" / "test_questions.json"
OUTPUT_FILE = ROOT / "results" / "candidate_mappings.json"

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2:latest"


def extract_question(text):
    if "<human>:" in text:
        text = text.split("<human>:", 1)[1]

    if "<bot>:" in text:
        text = text.split("<bot>:", 1)[0]

    return text.strip()


def ask_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]


def main():
    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        test_questions = json.load(file)

    document_questions = []

    for document in documents:
        document_questions.append(
            {
                "doc_id": document["doc_id"],
                "question": extract_question(
                    document.get("text", "")
                )
            }
        )

    documents_text = "\n".join(
        f"{item['doc_id']} | {item['question']}"
        for item in document_questions
    )

    results = []

    for number, test in enumerate(test_questions, start=1):
        question = test["question"]

        prompt = f"""
You are auditing the ground-truth labels of a semantic search evaluation dataset.

The user question is a paraphrase of one of the questions in the knowledge base.

Your task is to identify the 5 MOST SEMANTICALLY RELEVANT documents.

Important rules:

1. Compare the meaning of the user question with the meaning of each document question.
2. Do not choose a document merely because it shares one or two words.
3. Prefer the document that answers the user's question directly.
4. Treat paraphrases as equivalent when they have the same meaning.
5. If several documents cover the same topic, rank the most directly relevant one first.
6. Do not assume that the existing expected document ID is correct.
7. Only select document IDs that actually appear in the AVAILABLE DOCUMENTS list.
8. Return exactly 5 different document IDs.

USER QUESTION:
{question}

AVAILABLE DOCUMENTS:
{documents_text}

Return ONLY valid JSON in this exact format:

[
  {{
    "doc_id": "HR_001",
    "reason": "This document directly addresses the user's question."
  }},
  {{
    "doc_id": "HR_002",
    "reason": "This document addresses a closely related topic."
  }},
  {{
    "doc_id": "HR_003",
    "reason": "This document contains related policy information."
  }},
  {{
    "doc_id": "HR_004",
    "reason": "This document is relevant but less direct."
  }},
  {{
    "doc_id": "HR_005",
    "reason": "This document has some related information."
  }}
]

Do not add markdown.
Do not add any text outside the JSON.
"""

        print()
        print("=" * 80)
        print(f"QUESTION {number}: {question}")
        print("=" * 80)

        try:
            answer = ask_ollama(prompt)

            start = answer.find("[")
            end = answer.rfind("]")

            if start == -1 or end == -1:
                raise ValueError(
                    "Ollama did not return valid JSON."
                )

            candidates = json.loads(
                answer[start:end + 1]
            )

            if not isinstance(candidates, list):
                raise ValueError(
                    "Ollama response is not a JSON list."
                )

            valid_ids = {
                item["doc_id"]
                for item in document_questions
            }

            candidates = [
                candidate
                for candidate in candidates
                if candidate.get("doc_id") in valid_ids
            ]

        except Exception as error:
            print("ERROR:", error)
            candidates = []

        print("OLD EXPECTED:")
        print(
            ", ".join(
                test.get("relevant_doc_ids", [])
            )
        )

        print()
        print("OLLAMA CANDIDATES:")

        for rank, candidate in enumerate(
            candidates,
            start=1
        ):
            print(
                f"{rank}. "
                f"{candidate.get('doc_id')} | "
                f"{candidate.get('reason')}"
            )

        results.append(
            {
                "question_number": number,
                "question": question,
                "old_expected_doc_ids": test.get(
                    "relevant_doc_ids",
                    []
                ),
                "candidates": candidates
            }
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 80)
    print("MAPPING COMPLETE")
    print("=" * 80)
    print()
    print("Total questions:", len(results))
    print("Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
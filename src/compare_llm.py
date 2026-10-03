import csv
import os
import time

from dotenv import load_dotenv

import rag
import rag_gemini_legacy


load_dotenv()


QUESTIONS = [
    (
        "Normal question",
        "What is the company's policy on discrimination?"
    ),
    (
        "Paraphrased question",
        "How does the organization address discrimination?"
    ),
    (
        "Multiple-document question",
        "What are the purpose and benefits of the employee induction policy?"
    ),
    (
        "Missing information",
        "What is the company's policy for employee housing loans?"
    ),
    (
        "Partial-information question",
        "What is the work-from-home allowance and what is the employee housing loan amount?"
    )
]

OUTPUT_FILE = "results/llm_comparison.csv"


def run(provider, question, function):
    start = time.perf_counter()

    try:
        result = function(question)
        elapsed = time.perf_counter() - start

        return {
            "provider": provider,
            "question": question,
            "latency_seconds": round(elapsed, 3),
            "answer": result.get("answer", ""),
            "sources": ", ".join(result.get("sources", [])),
            "status": "success"
        }

    except Exception as exc:
        elapsed = time.perf_counter() - start

        return {
            "provider": provider,
            "question": question,
            "latency_seconds": round(elapsed, 3),
            "answer": "",
            "sources": "",
            "status": f"error: {exc}"
        }


def main():

    os.makedirs(
        "results",
        exist_ok=True
    )

    rows = []

    print("=" * 70)
    print("GEMINI VS OLLAMA RAG COMPARISON")
    print("=" * 70)

    print(
        "Ollama model:",
        os.getenv("OLLAMA_MODEL", "llama3.2")
    )

    for name, question in QUESTIONS:

        print()
        print("-" * 70)
        print(name)
        print("Question:", question)

        ollama_result = run(
            "Ollama",
            question,
            rag.ask_question
        )

        gemini_result = run(
            "Gemini",
            question,
            rag_gemini_legacy.ask_question
        )

        rows.extend(
            [ollama_result, gemini_result]
        )

        print()
        print("Ollama answer:")
        print(ollama_result["answer"])

        print()
        print("Gemini answer:")
        print(gemini_result["answer"])

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "provider",
                "question",
                "latency_seconds",
                "answer",
                "sources",
                "status"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 70)
    print("COMPARISON COMPLETED")
    print("=" * 70)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

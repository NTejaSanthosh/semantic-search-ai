import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_FILE = ROOT / "data" / "documents.json"
QUESTIONS_FILE = ROOT / "data" / "test_questions.json"
OUTPUT_FILE = ROOT / "results" / "mapping_audit.json"


def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stop_words = {
        "what", "are", "the", "is", "a", "an", "to", "of",
        "for", "and", "does", "do", "how", "can", "company",
        "organization", "employees", "employee", "their", "they",
        "its", "in", "on", "at", "be", "with", "from", "by",
        "should", "would", "regarding", "about"
    }
    return [word for word in words if word not in stop_words and len(word) > 2]


def get_document_text(document):
    return document.get("text", "")


def get_document_question(document):
    text = get_document_text(document)

    match = re.search(
        r"<human>:\s*(.*?)\s*<bot>:",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return text.strip()


def lexical_score(question, document_question):
    question_tokens = tokenize(question)
    document_tokens = tokenize(document_question)

    if not question_tokens or not document_tokens:
        return 0.0

    q_counter = Counter(question_tokens)
    d_counter = Counter(document_tokens)

    overlap = sum(
        min(q_counter[word], d_counter[word])
        for word in q_counter
        if word in d_counter
    )

    question_unique = set(question_tokens)
    document_unique = set(document_tokens)

    intersection = len(question_unique & document_unique)
    union = len(question_unique | document_unique)

    jaccard = intersection / union if union else 0.0
    coverage = overlap / len(question_tokens)

    return (jaccard * 0.4) + (coverage * 0.6)


def main():
    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    documents_by_id = {
        document.get("doc_id"): document
        for document in documents
    }

    audit_results = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        expected_ids = item.get("relevant_doc_ids", [])

        expected_documents = []

        for doc_id in expected_ids:
            document = documents_by_id.get(doc_id)

            if document:
                expected_documents.append({
                    "doc_id": doc_id,
                    "document_question": get_document_question(document)
                })
            else:
                expected_documents.append({
                    "doc_id": doc_id,
                    "document_question": "DOCUMENT NOT FOUND"
                })

        candidates = []

        for document in documents:
            document_question = get_document_question(document)

            score = lexical_score(
                question,
                document_question
            )

            candidates.append({
                "doc_id": document.get("doc_id"),
                "document_question": document_question,
                "score": round(score, 4)
            })

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        top_candidates = candidates[:5]

        expected_score = 0.0

        if expected_documents:
            expected_score = max(
                lexical_score(
                    question,
                    item["document_question"]
                )
                for item in expected_documents
                if item["document_question"] != "DOCUMENT NOT FOUND"
            )

        top_doc_ids = [
            candidate["doc_id"]
            for candidate in top_candidates
        ]

        expected_found = any(
            doc_id in top_doc_ids
            for doc_id in expected_ids
        )

        status = "LIKELY_OK"

        if expected_score < 0.10:
            status = "REVIEW"

        if not expected_found:
            status = "REVIEW"

        audit_results.append({
            "question_number": index,
            "question": question,
            "expected_doc_ids": expected_ids,
            "expected_documents": expected_documents,
            "expected_score": round(expected_score, 4),
            "top_candidates": top_candidates,
            "status": status
        })

    review_count = sum(
        1
        for result in audit_results
        if result["status"] == "REVIEW"
    )

    output = {
        "total_questions": len(audit_results),
        "questions_needing_review": review_count,
        "results": audit_results
    }

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
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 80)
    print("TEST MAPPING AUDIT")
    print("=" * 80)
    print()
    print("Total questions:", len(audit_results))
    print("Questions needing review:", review_count)
    print()
    print("-" * 80)

    for result in audit_results:
        if result["status"] != "REVIEW":
            continue

        print()
        print(
            f"QUESTION {result['question_number']}: "
            f"{result['question']}"
        )

        print(
            "EXPECTED:",
            ", ".join(result["expected_doc_ids"])
        )

        for candidate in result["top_candidates"][:3]:
            print(
                f"  CANDIDATE {candidate['doc_id']} "
                f"score={candidate['score']}: "
                f"{candidate['document_question']}"
            )

        print(
            "EXPECTED SCORE:",
            result["expected_score"]
        )

        print("-" * 80)

    print()
    print("Full audit saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
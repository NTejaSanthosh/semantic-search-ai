import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

with open(ROOT / "data" / "documents.json", "r", encoding="utf-8") as file:
    documents = json.load(file)

with open(ROOT / "data" / "test_questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

documents_by_id = {
    item["doc_id"]: item
    for item in documents
}


def extract_question(text):
    match = re.search(
        r"<human>:\s*(.*?)\s*<bot>:",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return text.strip()


print("=" * 100)
print("TEST QUESTION - EXPECTED DOCUMENT CONTENT")
print("=" * 100)

for number, item in enumerate(questions, start=1):
    expected_ids = item.get("relevant_doc_ids", [])

    print()
    print(f"QUESTION {number}")
    print("TEST QUESTION:")
    print(item["question"])

    print()
    print("EXPECTED DOCUMENT(S):")

    for doc_id in expected_ids:
        document = documents_by_id.get(doc_id)

        if not document:
            print(f"{doc_id}: DOCUMENT NOT FOUND")
            continue

        document_question = extract_question(
            document.get("text", "")
        )

        print(f"{doc_id}: {document_question}")

    print("-" * 100)
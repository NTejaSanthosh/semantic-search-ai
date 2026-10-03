import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

input_file = ROOT / "data" / "documents.json"
output_file = ROOT / "results" / "all_documents_questions.txt"

with open(input_file, "r", encoding="utf-8") as file:
    documents = json.load(file)

with open(output_file, "w", encoding="utf-8") as file:
    file.write(f"Documents: {len(documents)}\n")
    file.write("=" * 100 + "\n\n")

    for document in documents:
        doc_id = document.get("doc_id", "")

        text = document.get("text", "")

        if "<bot>:" in text:
            question = text.split("<bot>:", 1)[0]
        else:
            question = text

        question = question.replace("<human>:", "").strip()

        file.write(f"{doc_id} | {question}\n")

print(f"Documents: {len(documents)}")
print(f"Saved to: {output_file}")
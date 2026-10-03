import json
import re

with open("data/documents.json", "r", encoding="utf-8") as file:
    documents = json.load(file)

print("=" * 70)
print("FIRST 40 DOCUMENT QUESTIONS")
print("=" * 70)

for document in documents[:40]:

    match = re.search(
        r"<human>:\s*(.*?)\n",
        document["text"]
    )

    if match:
        question = match.group(1).strip()
    else:
        question = document["text"][:150]

    print(f"{document['doc_id']}: {question}")
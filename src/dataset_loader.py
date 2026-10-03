from datasets import load_dataset
import json
import os


DATASET_NAME = "EmbraceCoder/HR_Policy"
NUMBER_OF_DOCUMENTS = 120
OUTPUT_FILE = "data/documents.json"


def load_documents():

    print("Loading HR Policy dataset from Hugging Face...")

    dataset = load_dataset(
        DATASET_NAME,
        split="train"
    )

    documents = []

    print("Selecting 120 documents...")

    for index, row in enumerate(dataset):

        if not row["text"]:
            continue

        document = {
            "doc_id": f"HR_{index + 1:03d}",
            "title": f"HR Policy Document {index + 1}",
            "category": "HR",
            "source": "EmbraceCoder/HR_Policy",
            "text": row["text"]
        }

        documents.append(document)

        if len(documents) >= NUMBER_OF_DOCUMENTS:
            break

    return documents


def save_documents(documents):

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(
            documents,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Documents saved successfully!")
    print("Total documents:", len(documents))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":

    documents = load_documents()

    save_documents(documents)
import json
import re


INPUT_FILE = "data/documents.json"
OUTPUT_FILE = "data/test_questions.json"

NUMBER_OF_QUESTIONS = 40


def extract_question(text):

    match = re.search(
        r"<human>:\s*(.*?)(?:\n|$)",
        text
    )

    if match:
        return match.group(1).strip()

    return text.strip()


def main():

    print("Loading documents...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    test_questions = []

    for document in documents[:NUMBER_OF_QUESTIONS]:

        question = extract_question(
            document["text"]
        )

        test_questions.append({
            "question": question,
            "relevant_doc_ids": [
                document["doc_id"]
            ]
        })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            test_questions,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("Evaluation dataset created!")
    print("Number of questions:", len(test_questions))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
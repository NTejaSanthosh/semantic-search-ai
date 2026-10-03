from dynamic_kb import add_document, delete_document
from rag import ask_question


OLD_DOCUMENT_ID = "TEST_WFH_OLD"
NEW_DOCUMENT_ID = "TEST_WFH_NEW"


def clean_test_documents():

    print("=" * 70)
    print("CLEANING OLD TEST DOCUMENTS")
    print("=" * 70)

    delete_document(OLD_DOCUMENT_ID)
    delete_document(NEW_DOCUMENT_ID)


def create_conflicting_documents():

    print("\n" + "=" * 70)
    print("CREATING CONFLICTING DOCUMENTS")
    print("=" * 70)

    add_document(
        doc_id=OLD_DOCUMENT_ID,
        title="Work From Home Policy - 2025",
        category="Employee Benefits",
        source="HR Policy Manual 2025",
        text="""
The work-from-home allowance for eligible employees is
Rs. 2000 per month.

This policy is applicable from January 1, 2025.
""".strip(),
        date="2025-01-01",
        version="1.0"
    )

    add_document(
        doc_id=NEW_DOCUMENT_ID,
        title="Work From Home Policy - 2026",
        category="Employee Benefits",
        source="HR Policy Manual 2026",
        text="""
The work-from-home allowance for eligible employees is
Rs. 3000 per month.

This policy replaces the previous work-from-home allowance
of Rs. 2000 per month.

This updated policy is applicable from January 1, 2026.
Version 2.0.
""".strip(),
        date="2026-01-01",
        version="2.0"
    )


def test_conflict():

    print("\n" + "=" * 70)
    print("CONFLICT TEST")
    print("=" * 70)

    question = "What is the current work-from-home allowance?"

    print("Question:", question)

    result = ask_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nRetrieved Sources:")

    if result["results"]:

        for item in result["results"]:

            print()
            print("Document ID:", item.get("doc_id"))
            print("Title:", item.get("title"))
            print("Date:", item.get("date"))
            print("Version:", item.get("version"))
            print(
                "Similarity:",
                item.get("similarity")
            )
            print(
                "Rerank Score:",
                item.get("rerank_score")
            )

    else:

        print("No documents retrieved.")


def main():

    clean_test_documents()

    create_conflicting_documents()

    test_conflict()

    print("\n" + "=" * 70)
    print("CONFLICT TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
from rag.retriever import RAGRetriever


def main():
    retriever = RAGRetriever(top_k=3)

    queries = [
        "What should happen when a project is delayed?",
        "What is the task management policy?",
        "How should employee workload be handled?"
    ]

    for query in queries:
        print()
        print("=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        results = retriever.search(query)

        for index, result in enumerate(results, start=1):
            print()
            print(f"RESULT {index}")
            print("Score:", result["score"])
            print("Source:", result["source"])
            print("Text:", result["text"][:500])


if __name__ == "__main__":
    main()
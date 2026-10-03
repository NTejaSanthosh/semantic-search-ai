from multi_agent.rag_agent import RAGAgent


def main():
    agent = RAGAgent()

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

        result = agent.handle(
            query,
            employee_id="E001"
        )

        print()
        print("ANSWER:")
        print(result.get("answer"))

        print()
        print("SOURCES:")
        print(result.get("sources"))

        print()
        print("FULL RESULT:")
        print(result)


if __name__ == "__main__":
    main()
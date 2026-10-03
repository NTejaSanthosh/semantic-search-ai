from multi_agent.source_router import SourceRouter


def main():
    router = SourceRouter()

    queries = [
        "Show overdue tasks for P006",
        "What is the company escalation policy?",
        "P006 is delayed. What should we do according to the project delay guidelines?",
        "Who is assigned to T111?",
        "What are the workload guidelines?"
    ]

    for query in queries:
        source = router.decide(query)

        print()
        print("=" * 70)
        print("QUERY:", query)
        print("SOURCE:", source)


if __name__ == "__main__":
    main()
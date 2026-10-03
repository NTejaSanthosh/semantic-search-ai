from multi_agent.coordinator_agent import CoordinatorAgent


def main():

    coordinator = CoordinatorAgent()

    print("=" * 60)
    print(
        "Project Management Multi-Agent System"
    )
    print("=" * 60)

    employee_id = input(
        "Enter your employee ID: "
    ).strip().upper()

    print()

    while True:

        query = input(
            "Enter your query: "
        ).strip()

        if query.lower() in {
            "exit",
            "quit"
        }:

            print(
                "Exiting..."
            )

            break

        result = coordinator.handle(
            query,
            employee_id=employee_id
        )

        print()
        print(
            "Employee ID:"
        )
        print(
            result.get(
                "employee_id"
            )
        )

        print()
        print(
            "Access Role:"
        )
        print(
            result.get(
                "access_role"
            )
        )

        print()
        print(
            "Routing:"
        )
        print(
            result.get(
                "routing"
            )
        )

        print()
        print(
            "Execution Order:"
        )
        print(
            result.get(
                "execution_order"
            )
        )

        print()
        print(
            "Tool Calls:"
        )
        print(
            result.get(
                "tool_calls"
            )
        )

        print()
        print(
            "Final Answer:"
        )
        print(
            result.get(
                "final_answer"
            )
        )

        print()
        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()
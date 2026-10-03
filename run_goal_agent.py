from goal_agent import GoalOrientedAgent


def confirm_action(
    tool_name,
    arguments
):

    print("\nThe agent wants to perform")
    print("an impactful operation.")

    print(
        f"Tool: {tool_name}"
    )

    print(
        f"Arguments: {arguments}"
    )

    answer = input(
        "\nApprove this action? "
        "(yes/no): "
    ).strip().lower()

    return answer in [
        "yes",
        "y"
    ]


def main():

    print("=" * 70)
    print("GOAL-ORIENTED PROJECT MANAGEMENT AGENT")
    print("=" * 70)

    print(
        "\nExamples:"
    )

    print(
        "1. Show me all the projects."
    )

    print(
        "2. Find the delayed projects and "
        "identify their main risks."
    )

    print(
        "3. Find delayed projects, analyze "
        "their causes, and recommend actions."
    )

    print(
        "4. Analyze the projects and determine "
        "which one needs the most attention."
    )

    print(
        "\nType your own goal."
    )

    goal = input(
        "\nEnter goal: "
    ).strip()

    if not goal:

        print(
            "No goal provided."
        )

        return

    agent = GoalOrientedAgent()

    result = agent.run(
        goal,
        confirm_action=confirm_action
    )

    print(
        "\n" + "=" * 70
    )

    print("EXECUTION SUMMARY")

    print("=" * 70)

    state = result.get(
        "state",
        {}
    )

    print(
        f"Iterations: "
        f"{state.get('iteration', 0)}"
    )

    print(
        f"Tool calls: "
        f"{len(state.get('tool_history', []))}"
    )

    print(
        f"Tool failures: "
        f"{len(state.get('failed_tools', []))}"
    )

    print(
        f"Facts collected: "
        f"{len(state.get('facts', []))}"
    )


if __name__ == "__main__":

    main()
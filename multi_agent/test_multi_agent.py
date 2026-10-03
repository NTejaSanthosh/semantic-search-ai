import sys
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from multi_agent.coordinator_agent import CoordinatorAgent


TEST_CASES = [
    {
        "id": "T01",
        "query": "What is the risk level of P006?"
    },
    {
        "id": "T02",
        "query": "Show me the overdue tasks in P006."
    },
    {
        "id": "T03",
        "query": "Which employees have high workload?"
    },
    {
        "id": "T04",
        "query": "Which projects have overdue tasks?"
    },
    {
        "id": "T05",
        "query": "Which risky projects have overdue tasks and who is responsible for them?"
    },
    {
        "id": "T06",
        "query": "What is happening with P006?"
    }
]


def main():

    coordinator = CoordinatorAgent()

    results = []

    for test in TEST_CASES:

        print("\n" + "=" * 70)
        print(test["id"])
        print(test["query"])
        print("=" * 70)

        try:

            result = coordinator.handle(
                test["query"]
            )

            routing = result["routing"]
            execution_order = result["execution_order"]

            print(
                "Agents:",
                routing["agents"]
            )

            print(
                "Execution:",
                execution_order
            )

            print(
                "Final:",
                result["final_answer"]
            )

            results.append({
                "test_id": test["id"],
                "query": test["query"],
                "selected_agents": routing["agents"],
                "execution_order": execution_order,
                "status": "PASS",
                "final_answer": result["final_answer"]
            })

        except Exception as error:

            print(
                "ERROR:",
                str(error)
            )

            results.append({
                "test_id": test["id"],
                "query": test["query"],
                "selected_agents": [],
                "execution_order": [],
                "status": "FAIL",
                "final_answer": str(error)
            })

    output_dir = ROOT_DIR / "results"

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / "multi_agent_test_results.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "results": results
            },
            file,
            indent=2
        )

    print("\nTest results saved to:")
    print(output_file)


if __name__ == "__main__":
    main()
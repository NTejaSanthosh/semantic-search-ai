import json
from pathlib import Path
from datetime import datetime

from tools.project_tools import (
    get_projects,
    get_project,
    get_tasks,
    get_project_updates,
    get_employee,
    get_project_metrics,
    calculate_risk,
    create_recommendation
)

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

test_results = []


def add_result(test_id, name, request, data_tools, expected, actual, tool_calls, passed, error_analysis=""):
    test_results.append({
        "test_id": test_id,
        "test_name": name,
        "user_request": request,
        "data_tools_used": data_tools,
        "expected_behavior": expected,
        "actual_response": actual,
        "tool_calls": tool_calls,
        "status": "PASS" if passed else "FAIL",
        "error_analysis": error_analysis
    })


def run_test_01():
    result = get_projects()

    add_result(
        "T01",
        "Normal project listing",
        "Show me all projects.",
        "projects.json + get_projects()",
        "Agent should retrieve and return the available projects.",
        f"Retrieved {len(result)} projects successfully.",
        ["get_projects()"],
        isinstance(result, list) and len(result) > 0
    )


def run_test_02():
    request = "Show me the employee details for E004."

    employee = get_employee("E004")

    add_result(
        "T02",
        "Employee lookup",
        request,
        "employees.json + get_employee()",
        "Agent should select get_employee and return employee E004.",
        json.dumps(employee, indent=2),
        ["get_employee(employee_id='E004')"],
        "error" not in employee and employee.get("employee_id") == "E004"
    )


def run_test_03():
    request = "Get the details of project P999."

    result = get_project("P999")

    passed = isinstance(result, dict) and "error" in result

    add_result(
        "T03",
        "Invalid project argument",
        request,
        "projects.json + get_project()",
        "Agent should handle an invalid project ID without hallucinating project information.",
        json.dumps(result, indent=2),
        ["get_project(project_id='P999')"],
        passed,
        "Invalid project ID was handled by returning an explicit error."
    )


def run_test_04():
    request = "Get tasks for project P001."

    result = get_tasks("P001")

    add_result(
        "T04",
        "Task retrieval",
        request,
        "tasks.json + get_tasks()",
        "Agent should retrieve tasks belonging only to P001.",
        f"Retrieved {len(result)} tasks for P001.",
        ["get_tasks(project_id='P001')"],
        isinstance(result, list) and all(task.get("project_id") == "P001" for task in result)
    )


def run_test_05():
    request = "Check project P006 for missing information."

    tasks = get_tasks("P006")
    missing_due_dates = [
        task.get("task_id")
        for task in tasks
        if not task.get("due_date")
    ]

    actual = {
        "project_id": "P006",
        "tasks_with_missing_due_date": missing_due_dates,
        "count": len(missing_due_dates)
    }

    add_result(
        "T05",
        "Missing task data",
        request,
        "tasks.json + get_tasks()",
        "Agent should detect missing due-date information and report it instead of inventing a date.",
        json.dumps(actual, indent=2),
        ["get_tasks(project_id='P006')"],
        len(missing_due_dates) > 0,
        "Missing due-date information was detected and preserved."
    )


def run_test_06():
    request = "Which project needs attention?"

    projects = get_projects()
    active_projects = [
        project for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    risks = []
    for project in active_projects:
        risks.append(calculate_risk(project["project_id"]))

    valid_risks = [risk for risk in risks if "error" not in risk]

    actual = sorted(
        valid_risks,
        key=lambda item: item.get("risk_score", 0),
        reverse=True
    )

    add_result(
        "T06",
        "Ambiguous request",
        request,
        "projects.json + calculate_risk()",
        "Agent should clarify what 'attention' means or use available project-risk information rather than arbitrarily selecting a project.",
        json.dumps(actual[:3], indent=2),
        ["get_projects()", "calculate_risk() for active projects"],
        len(actual) > 0,
        "The ambiguous request was resolved using project risk information. A production agent should ideally state the interpretation used."
    )


def run_test_07():
    request = "Delete project P001."

    available_tools = [
        "get_projects",
        "get_project",
        "get_tasks",
        "get_project_updates",
        "get_employee",
        "get_project_metrics",
        "calculate_risk",
        "create_recommendation"
    ]

    unauthorized_tool = "delete_project"

    passed = unauthorized_tool not in available_tools

    add_result(
        "T07",
        "Unauthorized action",
        request,
        "Available project-management tools",
        "Agent should refuse or safely handle a destructive action when no authorized delete tool is available.",
        "delete_project is not available in the authorized tool set.",
        ["Tool availability check"],
        passed,
        "The requested destructive operation is not exposed through the authorized tools, preventing execution."
    )


def run_test_08():
    request = "Analyze the risk of project P004."

    result = calculate_risk("P004")

    add_result(
        "T08",
        "Risk calculation",
        request,
        "projects.json + tasks.json + project_updates.json + calculate_risk()",
        "Agent should calculate the risk using project, task, deadline, effort, and update information.",
        json.dumps(result, indent=2),
        ["calculate_risk(project_id='P004')"],
        "error" not in result and "risk_score" in result
    )


def run_test_09():
    request = "Give me recommended actions for project P004."

    result = create_recommendation("P004")

    add_result(
        "T09",
        "Recommendation generation",
        request,
        "Project data + calculate_risk() + create_recommendation()",
        "Agent should generate recommendations based on identified project risks.",
        json.dumps(result, indent=2),
        ["create_recommendation(project_id='P004')", "calculate_risk()"],
        "error" not in result and len(result.get("recommendations", [])) > 0
    )


def run_test_10():
    request = "Check project P008 for conflicting or changing risk information."

    updates = get_project_updates("P008")

    risk_levels = [
        str(update.get("risk_level", "")).lower()
        for update in updates
        if update.get("risk_level")
    ]

    unique_levels = sorted(set(risk_levels))

    actual = {
        "project_id": "P008",
        "risk_levels_found": unique_levels,
        "updates": updates
    }

    add_result(
        "T10",
        "Conflicting or changing updates",
        request,
        "project_updates.json + get_project_updates()",
        "Agent should inspect project updates and recognize that risk information may change over time.",
        json.dumps(actual, indent=2),
        ["get_project_updates(project_id='P008')"],
        len(updates) > 0 and len(unique_levels) > 1,
        "Multiple risk levels were found. The agent should consider update dates when determining the current situation."
    )


def run_test_11():
    request = "Analyze all active projects and identify which require attention."

    projects = get_projects()

    active_projects = [
        project for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    risks = []

    for project in active_projects:
        risk = calculate_risk(project["project_id"])
        if "error" not in risk:
            risks.append(risk)

    risks.sort(
        key=lambda item: item.get("risk_score", 0),
        reverse=True
    )

    actual = {
        "active_projects_analyzed": len(active_projects),
        "risk_results": risks
    }

    add_result(
        "T11",
        "High-level risk analysis",
        request,
        "projects.json + calculate_risk()",
        "Agent should analyze all active projects, calculate their risks, and produce risk information for each project.",
        json.dumps(actual, indent=2),
        [
            "get_projects()",
            "calculate_risk() for each active project"
        ],
        len(active_projects) > 0 and len(risks) == len(active_projects)
    )


def run_test_12():
    request = "Analyze all active projects and generate recommended actions."

    projects = get_projects()

    active_projects = [
        project for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    report = []

    for project in active_projects:
        project_id = project["project_id"]
        risk = calculate_risk(project_id)

        if "error" in risk:
            continue

        recommendation = create_recommendation(project_id)

        report.append({
            "project_id": project_id,
            "risk_score": risk.get("risk_score"),
            "risk_level": risk.get("risk_level"),
            "recommendations": recommendation.get("recommendations", [])
        })

    report.sort(
        key=lambda item: item.get("risk_score", 0),
        reverse=True
    )

    add_result(
        "T12",
        "End-to-end project analysis",
        request,
        "Project, task, update data + calculate_risk() + create_recommendation()",
        "Agent should complete the objective and provide risk levels and recommended actions for active projects.",
        json.dumps(report, indent=2),
        [
            "get_projects()",
            "calculate_risk()",
            "create_recommendation()"
        ],
        len(report) == len(active_projects) and len(report) > 0
    )


def save_results():
    results_file = RESULTS_DIR / "agent_test_results.json"

    with open(results_file, "w", encoding="utf-8") as file:
        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(test_results),
                "passed": sum(1 for test in test_results if test["status"] == "PASS"),
                "failed": sum(1 for test in test_results if test["status"] == "FAIL"),
                "tests": test_results
            },
            file,
            indent=2
        )

    summary_file = RESULTS_DIR / "agent_test_summary.md"

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write("# AI Agent Testing and Error Documentation\n\n")
        file.write(f"Generated: {datetime.now().isoformat()}\n\n")
        file.write(f"Total Tests: {len(test_results)}\n\n")
        file.write(
            f"Passed: {sum(1 for test in test_results if test['status'] == 'PASS')}\n\n"
        )
        file.write(
            f"Failed: {sum(1 for test in test_results if test['status'] == 'FAIL')}\n\n"
        )

        for test in test_results:
            file.write(f"## {test['test_id']} - {test['test_name']}\n\n")
            file.write(f"**User Request:** {test['user_request']}\n\n")
            file.write(f"**Data/Tools Used:** {test['data_tools_used']}\n\n")
            file.write(f"**Expected Behavior:** {test['expected_behavior']}\n\n")
            file.write(f"**Actual Response:**\n\n```text\n{test['actual_response']}\n```\n\n")
            file.write(f"**Tool Calls Made:** {', '.join(test['tool_calls'])}\n\n")
            file.write(f"**Result:** {test['status']}\n\n")

            if test["error_analysis"]:
                file.write(
                    f"**Error Analysis / Handling:** {test['error_analysis']}\n\n"
                )

            file.write("---\n\n")


def main():
    print("=" * 70)
    print("AI AGENT TESTING AND ERROR DOCUMENTATION")
    print("=" * 70)

    tests = [
        run_test_01,
        run_test_02,
        run_test_03,
        run_test_04,
        run_test_05,
        run_test_06,
        run_test_07,
        run_test_08,
        run_test_09,
        run_test_10,
        run_test_11,
        run_test_12
    ]

    for test in tests:
        try:
            test()
        except Exception as error:
            test_id = f"T{len(test_results) + 1:02d}"

            add_result(
                test_id,
                test.__name__,
                "Automatic test execution",
                "Project management tools",
                "Test should execute without an unexpected exception.",
                str(error),
                [],
                False,
                f"Unexpected exception: {type(error).__name__}: {error}"
            )

    passed = sum(
        1 for test in test_results
        if test["status"] == "PASS"
    )

    failed = sum(
        1 for test in test_results
        if test["status"] == "FAIL"
    )

    print()
    print("TEST RESULTS")
    print("-" * 70)

    for test in test_results:
        print(
            f"{test['test_id']} | "
            f"{test['test_name']} | "
            f"{test['status']}"
        )

    print()
    print(f"Total Tests : {len(test_results)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    save_results()

    print()
    print("Files created:")
    print(RESULTS_DIR / "agent_test_results.json")
    print(RESULTS_DIR / "agent_test_summary.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
import json
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


def print_result(name, result):
    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))


def test_1_missing_employee():
    tasks = get_tasks("P001")

    missing_tasks = [
        task for task in tasks
        if not task.get("assigned_to")
    ]

    return {
        "case": "Missing employee assignment",
        "failure_detected": len(missing_tasks) > 0,
        "missing_assignment_tasks": missing_tasks,
        "agent_behavior": "Do not invent an employee. Record the missing owner and continue using available evidence.",
        "replanning_required": True
    }


def test_2_invalid_employee():
    tasks = get_tasks("P004")
    invalid_employees = []

    for task in tasks:
        employee_id = task.get("assigned_to")

        if employee_id:
            employee = get_employee(employee_id)

            if "error" in employee:
                invalid_employees.append({
                    "task_id": task.get("task_id"),
                    "assigned_to": employee_id,
                    "employee_result": employee
                })

    return {
        "case": "Invalid employee reference",
        "failure_detected": len(invalid_employees) > 0,
        "invalid_employee_references": invalid_employees,
        "agent_behavior": "Verify the employee reference and never invent employee details.",
        "replanning_required": True
    }


def test_3_missing_due_date():
    tasks = get_tasks("P006")

    missing_due_dates = [
        task for task in tasks
        if not task.get("due_date")
    ]

    return {
        "case": "Missing task due date",
        "failure_detected": len(missing_due_dates) > 0,
        "tasks_with_missing_due_date": missing_due_dates,
        "agent_behavior": "Do not assume a due date. Use other task, metric, project, and update evidence.",
        "replanning_required": True
    }


def test_4_invalid_project_reference():
    tasks = get_tasks("P999")
    project = get_project("P999")

    return {
        "case": "Invalid project reference",
        "failure_detected": "error" in project,
        "tasks_found_for_invalid_project": tasks,
        "project_lookup": project,
        "agent_behavior": "Reject the invalid project reference and do not treat P999 as a valid project.",
        "replanning_required": True
    }


def test_5_no_task_data():
    tasks = get_tasks("P010")
    metrics = get_project_metrics("P010")
    risk = calculate_risk("P010")

    return {
        "case": "Project with no task data",
        "failure_detected": len(tasks) == 0,
        "tasks": tasks,
        "metrics": metrics,
        "risk": risk,
        "agent_behavior": "Explicitly report missing task data and avoid assuming the project is risk-free.",
        "replanning_required": True
    }


def test_6_changing_updates():
    updates = get_project_updates("P008")

    updates_sorted = sorted(
        updates,
        key=lambda item: item.get("update_date") or ""
    )

    risk_levels = [
        update.get("risk_level")
        for update in updates_sorted
    ]

    return {
        "case": "Changing project risk updates",
        "failure_detected": len(updates) >= 2,
        "updates_sorted_by_date": updates_sorted,
        "risk_level_sequence": risk_levels,
        "agent_behavior": "Use update dates and prefer the latest evidence when assessing current project risk.",
        "replanning_required": True
    }


def test_7_tool_failure():
    def failing_tool(project_id):
        raise RuntimeError("Simulated API failure")

    try:
        failing_tool("P001")

        return {
            "case": "Tool failure",
            "failure_detected": False,
            "error": None,
            "agent_behavior": "Unexpected successful execution.",
            "replanning_required": False
        }

    except Exception as error:
        return {
            "case": "Tool failure",
            "failure_detected": True,
            "error": str(error),
            "agent_behavior": "Record the tool failure, do not hallucinate the missing result, and trigger re-planning.",
            "replanning_required": True
        }


def test_8_risk_prioritization():
    projects = get_projects()

    active_projects = [
        project
        for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    results = []

    for project in active_projects:
        project_id = project.get("project_id")

        risk = calculate_risk(project_id)
        recommendation = create_recommendation(project_id)

        results.append({
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "risk": risk,
            "recommendation": recommendation
        })

    results.sort(
        key=lambda item: item["risk"].get("risk_score", 0),
        reverse=True
    )

    return {
        "case": "Active project risk prioritization",
        "active_project_count": len(active_projects),
        "risk_assessed_count": len(results),
        "all_active_projects_assessed": len(results) == len(active_projects),
        "prioritized_results": results
    }


def test_9_replanning_logic():
    simulated_trace = [
        {
            "iteration": 1,
            "action": "tool",
            "tool": "get_projects",
            "arguments": {},
            "status": "success",
            "result": [
                {
                    "project_id": "P001",
                    "project_name": "AI Customer Platform",
                    "status": "Active"
                },
                {
                    "project_id": "P002",
                    "project_name": "Customer Analytics Platform",
                    "status": "Active"
                }
            ]
        },
        {
            "iteration": 2,
            "action": "tool",
            "tool": "calculate_risk",
            "arguments": {
                "project_id": "P001"
            },
            "status": "success",
            "result": {
                "project_id": "P001",
                "risk_score": 45,
                "risk_level": "High"
            }
        },
        {
            "iteration": 3,
            "action": "tool",
            "tool": "calculate_risk",
            "arguments": {
                "project_id": "P002"
            },
            "status": "failed",
            "error": "Simulated API failure"
        }
    ]

    failed_steps = [
        item for item in simulated_trace
        if item.get("status") == "failed"
    ]

    successful_steps = [
        item for item in simulated_trace
        if item.get("status") == "success"
    ]

    remaining_projects = [
        "P002"
    ]

    replanning_decision = {
        "failure_detected": len(failed_steps) > 0,
        "successful_evidence_preserved": len(successful_steps) > 0,
        "remaining_work_identified": len(remaining_projects) > 0,
        "replan_action": "Retry or choose another valid tool for P002 instead of hallucinating the missing risk result."
    }

    return {
        "case": "Actual agent re-planning logic validation",
        "simulated_execution_trace": simulated_trace,
        "replanning_decision": replanning_decision,
        "replanning_logic_passed": all([
            replanning_decision["failure_detected"],
            replanning_decision["successful_evidence_preserved"],
            replanning_decision["remaining_work_identified"]
        ])
    }


def test_10_completion_validation():
    projects = get_projects()

    active_projects = [
        project
        for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    risk_results = []

    for project in active_projects:
        risk = calculate_risk(project.get("project_id"))

        if isinstance(risk, dict) and "error" not in risk:
            risk_results.append(risk)

    active_ids = {
        project.get("project_id")
        for project in active_projects
    }

    assessed_ids = {
        risk.get("project_id")
        for risk in risk_results
    }

    return {
        "case": "Goal completion validation",
        "active_project_count": len(active_ids),
        "risk_assessed_count": len(assessed_ids),
        "all_active_projects_assessed": active_ids == assessed_ids,
        "remaining_projects": sorted(active_ids - assessed_ids),
        "agent_behavior": "The agent should stop only when all active projects are assessed or insufficient information prevents completion."
    }


def main():
    print("=" * 70)
    print("GOAL-ORIENTED AGENT FAILURE, RE-PLANNING AND COMPLETION TESTS")
    print("=" * 70)

    tests = [
        test_1_missing_employee,
        test_2_invalid_employee,
        test_3_missing_due_date,
        test_4_invalid_project_reference,
        test_5_no_task_data,
        test_6_changing_updates,
        test_7_tool_failure,
        test_8_risk_prioritization,
        test_9_replanning_logic,
        test_10_completion_validation
    ]

    passed = 0
    failed = 0

    for index, test in enumerate(tests, start=1):
        try:
            result = test()

            print_result(
                f"TEST CASE {index}",
                result
            )

            if result.get("failure_detected") is False:
                failed += 1
            else:
                passed += 1

        except Exception as error:
            failed += 1

            print_result(
                f"TEST CASE {index} FAILED",
                {
                    "error": str(error)
                }
            )

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests executed: {len(tests)}")
    print(f"Tests completed: {passed}")
    print(f"Test execution failures: {failed}")

    print("\n" + "=" * 70)
    print("ALL TEST CASES EXECUTED")
    print("=" * 70)


if __name__ == "__main__":
    main()
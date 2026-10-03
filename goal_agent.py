import json
import re
import ollama
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

MODEL = "qwen3:4b"

TOOLS = {
    "get_projects": get_projects,
    "get_project": get_project,
    "get_tasks": get_tasks,
    "get_project_updates": get_project_updates,
    "get_employee": get_employee,
    "get_project_metrics": get_project_metrics,
    "calculate_risk": calculate_risk,
    "create_recommendation": create_recommendation
}

TOOL_DESCRIPTIONS = {
    "get_projects": "Get all projects.",
    "get_project": "Get one project using project_id.",
    "get_tasks": "Get all tasks for a project using project_id.",
    "get_project_updates": "Get project updates using project_id.",
    "get_employee": "Get employee information using employee_id.",
    "get_project_metrics": "Calculate task metrics for a project using project_id.",
    "calculate_risk": "Calculate the risk score and risk level for a project using project_id.",
    "create_recommendation": "Create recommended actions for a project using project_id."
}

PLANNER_PROMPT = """
You are the planning component of a goal-oriented project management agent.

Goal:
Analyze all active projects and generate a prioritized risk report identifying which projects require immediate attention, why they are at risk, and recommended actions.

Create a dynamic execution plan.

The plan must:
1. Discover active projects.
2. Analyze every active project.
3. Use appropriate project, task, update, employee, metric, risk, and recommendation tools when needed.
4. Detect missing or invalid information.
5. Use dependencies between steps.
6. Gather deeper evidence for risky projects.
7. Prioritize projects by risk.
8. Produce a final grounded report.
9. Allow re-planning when a tool fails or information is missing.

Do not invent project IDs.
Do not invent employee IDs.
Do not invent risk information.

Return ONLY valid JSON.

Required format:
{
  "goal": "string",
  "steps": [
    {
      "step": 1,
      "purpose": "string",
      "tool": "tool_name",
      "arguments": {}
    }
  ]
}

Available tools:
""" + json.dumps(TOOL_DESCRIPTIONS, indent=2)


REPLAN_PROMPT = """
You are the re-planning component of a goal-oriented project management agent.

Original goal:
Analyze all active projects and generate a prioritized risk report identifying which projects require immediate attention, why they are at risk, and recommended actions.

The previous execution encountered a problem.

You must create a new plan that continues from the available evidence.

Rules:
- Do not repeat successful work unnecessarily.
- Do not invent missing information.
- Use only project IDs and employee IDs found in evidence.
- Every active project must eventually have a risk assessment.
- If a tool failed, choose another valid approach when possible.
- If information is missing, gather it with an available tool.
- If a project has no tasks, explicitly verify that condition.
- If an employee reference is invalid, verify it with get_employee.
- If updates change over time, inspect update dates and descriptions.
- The plan must move toward completing the original goal.

Return ONLY valid JSON.

Required format:
{
  "reason": "string",
  "steps": [
    {
      "step": 1,
      "purpose": "string",
      "tool": "tool_name",
      "arguments": {}
    }
  ]
}

Available tools:
""" + json.dumps(TOOL_DESCRIPTIONS, indent=2)


REPORT_PROMPT = """
You are the final reporting component of a goal-oriented project management agent.

Generate a prioritized risk report for the original goal:

Analyze all active projects and generate a prioritized risk report identifying which projects require immediate attention, why they are at risk, and recommended actions.

Use ONLY the supplied execution evidence.

Never invent:
- deadlines
- employees
- project status
- risks
- task information
- update information
- recommendations unsupported by evidence

The report must:
1. State how many active projects were analyzed.
2. List active projects in priority order.
3. Give each project a risk score and risk level when available.
4. Explain the evidence behind the risk.
5. Mention important task problems.
6. Mention important project update evidence.
7. Mention data-quality problems.
8. Give concrete recommended actions.
9. Clearly identify incomplete analysis if any project could not be analyzed.
10. Never treat a tool failure as successful evidence.

Use this structure:

# Prioritized Project Risk Report

## Executive Summary

## Priority 1
Project:
Risk:
Risk Score:
Why It Is At Risk:
Evidence:
Recommended Actions:

## Priority 2
...

## Data Quality and Exceptions

## Execution and Re-planning Summary

## Completion Status

Execution evidence:
"""


def clean_json_text(text):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE)
        text = re.sub(r"```$", "", text.strip())

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        return text[start:end + 1]

    return text


def parse_json_response(response):
    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        return None

    cleaned = clean_json_text(response)

    try:
        return json.loads(cleaned)
    except Exception:
        return None


def normalize_step(step):
    if not isinstance(step, dict):
        return None

    tool = step.get("tool") or step.get("tool_name") or step.get("name")
    arguments = step.get("arguments") or step.get("args") or {}

    if not isinstance(tool, str):
        return None

    tool = tool.strip()

    if tool not in TOOLS:
        return None

    if not isinstance(arguments, dict):
        arguments = {}

    return {
        "purpose": str(step.get("purpose", "Execute required project-management analysis.")),
        "tool": tool,
        "arguments": arguments
    }


def normalize_plan(plan):
    if not isinstance(plan, dict):
        return None

    raw_steps = plan.get("steps") or plan.get("plan") or []

    if isinstance(raw_steps, dict):
        raw_steps = [raw_steps]

    if not isinstance(raw_steps, list):
        return None

    steps = []

    for raw_step in raw_steps:
        normalized = normalize_step(raw_step)

        if normalized:
            normalized["step"] = len(steps) + 1
            steps.append(normalized)

    if not steps:
        return None

    return {
        "goal": plan.get(
            "goal",
            "Analyze all active projects and generate a prioritized risk report."
        ),
        "steps": steps
    }


def call_model(prompt, json_mode=False):
    options = {
        "temperature": 0.1,
        "num_predict": 1200
    }

    kwargs = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "options": options
    }

    if json_mode:
        kwargs["format"] = "json"

    response = ollama.chat(**kwargs)

    return response["message"]["content"]


def create_plan():
    for attempt in range(3):
        try:
            raw = call_model(PLANNER_PROMPT, json_mode=True)
            parsed = parse_json_response(raw)
            plan = normalize_plan(parsed)

            if plan:
                return plan

        except Exception:
            pass

    return {
        "goal": "Analyze all active projects and generate a prioritized risk report.",
        "steps": [
            {
                "step": 1,
                "purpose": "Discover all projects so active projects can be identified.",
                "tool": "get_projects",
                "arguments": {}
            }
        ]
    }


def compact_value(value, limit=1800):
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)

    if len(text) > limit:
        return text[:limit] + "...[truncated]"

    return text


def build_state(trace):
    successful_tools = []
    failed_tools = []
    risk_results = {}
    projects = []
    active_projects = []

    for item in trace:
        action = item.get("action")

        if action == "tool":
            tool = item.get("tool")
            result = item.get("result")

            if item.get("status") == "success":
                successful_tools.append(
                    {
                        "tool": tool,
                        "arguments": item.get("arguments", {})
                    }
                )

                if tool == "get_projects" and isinstance(result, list):
                    projects = result
                    active_projects = [
                        p for p in result
                        if str(p.get("status", "")).lower() == "active"
                    ]

                if tool == "calculate_risk" and isinstance(result, dict):
                    project_id = result.get("project_id")

                    if project_id:
                        risk_results[project_id] = {
                            "risk_score": result.get("risk_score"),
                            "risk_level": result.get("risk_level"),
                            "reasons": result.get("reasons", [])
                        }

            else:
                failed_tools.append(
                    {
                        "tool": tool,
                        "arguments": item.get("arguments", {}),
                        "error": item.get("error")
                    }
                )

    analyzed_ids = sorted(risk_results.keys())

    return {
        "successful_tools": successful_tools[-30:],
        "failed_tools": failed_tools[-15:],
        "active_projects": [
            {
                "project_id": p.get("project_id"),
                "project_name": p.get("project_name"),
                "deadline": p.get("deadline"),
                "status": p.get("status")
            }
            for p in active_projects
        ],
        "risk_results": risk_results,
        "risk_assessed_project_ids": analyzed_ids,
        "remaining_active_project_ids": [
            p.get("project_id")
            for p in active_projects
            if p.get("project_id") not in analyzed_ids
        ]
    }


def execute_tool(tool_name, arguments):
    if tool_name not in TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        result = TOOLS[tool_name](**arguments)

        if isinstance(result, dict) and "error" in result:
            return {
                "success": False,
                "error": result.get("error"),
                "result": result
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def expand_plan_after_projects(plan, projects):
    active_projects = [
        project
        for project in projects
        if str(project.get("status", "")).lower() == "active"
    ]

    expanded_steps = []
    step_number = 1

    for step in plan.get("steps", []):
        if step["tool"] != "get_projects":
            expanded_steps.append(
                {
                    "step": step_number,
                    "purpose": step["purpose"],
                    "tool": step["tool"],
                    "arguments": step["arguments"]
                }
            )
            step_number += 1

    for project in active_projects:
        project_id = project.get("project_id")

        expanded_steps.append(
            {
                "step": step_number,
                "purpose": f"Assess risk for active project {project_id}.",
                "tool": "calculate_risk",
                "arguments": {
                    "project_id": project_id
                }
            }
        )

        step_number += 1

    return expanded_steps


def should_gather_details(risk):
    if not isinstance(risk, dict):
        return False

    level = str(risk.get("risk_level", "")).lower()

    try:
        score = float(risk.get("risk_score", 0))
    except Exception:
        score = 0

    return level in {"critical", "high"} or score >= 40


def generate_replan(state, problem):
    prompt = (
        REPLAN_PROMPT
        + "\n\nCurrent execution state:\n"
        + json.dumps(state, indent=2, default=str)
        + "\n\nProblem encountered:\n"
        + str(problem)
    )

    for _ in range(3):
        try:
            raw = call_model(prompt, json_mode=True)
            parsed = parse_json_response(raw)
            plan = normalize_plan(parsed)

            if plan:
                return plan

        except Exception:
            pass

    remaining = state.get("remaining_active_project_ids", [])

    if remaining:
        return {
            "reason": "Continue risk assessment for projects that have not yet been assessed.",
            "steps": [
                {
                    "step": index + 1,
                    "purpose": f"Assess remaining active project {project_id}.",
                    "tool": "calculate_risk",
                    "arguments": {
                        "project_id": project_id
                    }
                }
                for index, project_id in enumerate(remaining)
            ]
        }

    return None


def generate_final_report(trace):
    evidence = []

    for item in trace:
        if item.get("action") == "tool":
            evidence.append(
                {
                    "iteration": item.get("iteration"),
                    "tool": item.get("tool"),
                    "arguments": item.get("arguments"),
                    "status": item.get("status"),
                    "result": item.get("result"),
                    "error": item.get("error")
                }
            )

    prompt = (
        REPORT_PROMPT
        + "\n\n"
        + json.dumps(evidence, indent=2, default=str)
    )

    for _ in range(3):
        try:
            report = call_model(prompt, json_mode=False)

            if report and len(report.strip()) > 100:
                return report.strip()

        except Exception:
            pass

    state = build_state(trace)

    lines = [
        "# Prioritized Project Risk Report",
        "",
        "## Executive Summary",
        "",
        f"Active projects risk-assessed: {len(state['risk_results'])}",
        "",
        "## Risk Priorities",
        ""
    ]

    sorted_risks = sorted(
        state["risk_results"].items(),
        key=lambda item: item[1].get("risk_score", 0) or 0,
        reverse=True
    )

    for index, (project_id, risk) in enumerate(sorted_risks, start=1):
        lines.append(
            f"{index}. {project_id} — {risk.get('risk_level')} "
            f"— score {risk.get('risk_score')}"
        )
        for reason in risk.get("reasons", []):
            lines.append(f"   - {reason}")

    lines.extend(
        [
            "",
            "## Completion Status",
            "",
            f"Risk-assessed projects: {len(state['risk_assessed_project_ids'])}",
            f"Remaining active projects: {len(state['remaining_active_project_ids'])}"
        ]
    )

    return "\n".join(lines)


def run_agent(max_iterations=40, max_replans=8):
    print("=" * 70)
    print("GOAL-ORIENTED PROJECT MANAGEMENT AGENT")
    print("=" * 70)

    print("\nGENERATING DYNAMIC PLAN")
    plan = create_plan()

    print(json.dumps(plan, indent=2, default=str))

    trace = []
    current_steps = plan["steps"]
    step_index = 0
    replans = 0
    iteration = 0
    discovered_projects = False

    while iteration < max_iterations:
        if step_index >= len(current_steps):
            state = build_state(trace)

            if state["remaining_active_project_ids"]:
                if replans >= max_replans:
                    break

                new_plan = generate_replan(
                    state,
                    "The current plan finished but some active projects still lack risk assessment."
                )

                replans += 1

                if not new_plan:
                    break

                print("\n" + "=" * 70)
                print("RE-PLANNING")
                print("=" * 70)
                print(json.dumps(new_plan, indent=2, default=str))

                current_steps = new_plan["steps"]
                step_index = 0
                continue

            break

        step = current_steps[step_index]
        step_index += 1
        iteration += 1

        tool_name = step.get("tool")
        arguments = step.get("arguments", {})

        print("\n" + "=" * 70)
        print(f"ITERATION {iteration}")
        print("=" * 70)
        print(f"Purpose: {step.get('purpose')}")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {json.dumps(arguments)}")

        result = execute_tool(tool_name, arguments)

        if result["success"]:
            trace.append(
                {
                    "iteration": iteration,
                    "action": "tool",
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "success",
                    "result": result["result"]
                }
            )

            print("Status: SUCCESS")
            print(compact_value(result["result"]))

            if tool_name == "get_projects":
                discovered_projects = True

                if isinstance(result["result"], list):
                    current_steps = expand_plan_after_projects(
                        plan,
                        result["result"]
                    )
                    step_index = 0
                    plan = {
                        "goal": plan.get("goal"),
                        "steps": current_steps
                    }

                    continue

            if tool_name == "calculate_risk":
                risk = result["result"]

                if should_gather_details(risk):
                    project_id = risk.get("project_id")

                    detail_steps = [
                        {
                            "step": 1,
                            "purpose": f"Inspect task-level evidence for risky project {project_id}.",
                            "tool": "get_tasks",
                            "arguments": {
                                "project_id": project_id
                            }
                        },
                        {
                            "step": 2,
                            "purpose": f"Inspect dated project updates for risky project {project_id}.",
                            "tool": "get_project_updates",
                            "arguments": {
                                "project_id": project_id
                            }
                        },
                        {
                            "step": 3,
                            "purpose": f"Generate recommended actions for risky project {project_id}.",
                            "tool": "create_recommendation",
                            "arguments": {
                                "project_id": project_id
                            }
                        }
                    ]

                    current_steps[step_index:step_index] = detail_steps

        else:
            trace.append(
                {
                    "iteration": iteration,
                    "action": "tool",
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "failed",
                    "error": result.get("error")
                }
            )

            print("Status: FAILED")
            print(f"Error: {result.get('error')}")

            if replans < max_replans:
                state = build_state(trace)

                new_plan = generate_replan(
                    state,
                    result.get("error")
                )

                replans += 1

                if new_plan:
                    print("\n" + "=" * 70)
                    print("RE-PLANNING AFTER FAILURE")
                    print("=" * 70)
                    print(json.dumps(new_plan, indent=2, default=str))

                    current_steps = new_plan["steps"]
                    step_index = 0

    state = build_state(trace)

    print("\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Iterations used: {iteration}")
    print(f"Re-plans used: {replans}")
    print(f"Active projects discovered: {len(state['active_projects'])}")
    print(f"Projects risk-assessed: {len(state['risk_assessed_project_ids'])}")
    print(
        f"Projects remaining: "
        f"{len(state['remaining_active_project_ids'])}"
    )

    print("\n" + "=" * 70)
    print("EXECUTION TRACE")
    print("=" * 70)
    print(json.dumps(trace, indent=2, default=str))

    print("\n" + "=" * 70)
    print("GENERATING FINAL RISK REPORT")
    print("=" * 70)

    report = generate_final_report(trace)

    print("\n" + "=" * 70)
    print("FINAL PRIORITIZED RISK REPORT")
    print("=" * 70)
    print(report)

    return {
        "plan": plan,
        "trace": trace,
        "state": state,
        "report": report
    }


def main():
    run_agent()


if __name__ == "__main__":
    main()
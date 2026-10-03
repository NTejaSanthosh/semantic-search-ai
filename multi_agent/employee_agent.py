import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.project_tools import (
    get_projects,
    get_tasks,
    get_employee
)

from multi_agent.rbac import (
    Permission,
    has_permission
)


class EmployeeAgent:

    def __init__(self):
        self.name = "Employee Agent"

    def check_permission(
        self,
        employee_id,
        permission
    ):

        result = has_permission(
            employee_id,
            permission
        )

        if not result["allowed"]:

            return {
                "allowed": False,
                "reason": result["reason"]
            }

        return {
            "allowed": True
        }

    def call_tool(
        self,
        tool_guard,
        tool_name,
        tool_function,
        arguments
    ):

        guard_result = tool_guard.can_call(
            tool_name,
            arguments
        )

        if not guard_result["allowed"]:

            return {
                "success": False,
                "error": guard_result["reason"],
                "guardrail_status": guard_result["status"]
            }

        try:

            result = tool_function(
                **arguments
            )

            tool_guard.record_call(
                tool_name,
                arguments
            )

            return result

        except Exception as error:

            return {
                "success": False,
                "error": "Tool execution failed",
                "details": str(error),
                "tool": tool_name
            }

    def calculate_workload(
        self,
        project_ids,
        tool_guard
    ):

        employees = {}

        for project_id in project_ids:

            tasks = self.call_tool(
                tool_guard,
                "get_tasks",
                get_tasks,
                {
                    "project_id": project_id
                }
            )

            if not isinstance(
                tasks,
                list
            ):

                continue

            for task in tasks:

                employee_id = task.get(
                    "assigned_to"
                )

                if not employee_id:
                    continue

                if employee_id not in employees:

                    employees[
                        employee_id
                    ] = {
                        "employee_id": employee_id,
                        "task_count": 0,
                        "actual_hours": 0,
                        "tasks": []
                    }

                employees[
                    employee_id
                ][
                    "task_count"
                ] += 1

                employees[
                    employee_id
                ][
                    "actual_hours"
                ] += (
                    task.get(
                        "actual_hours"
                    ) or 0
                )

                employees[
                    employee_id
                ][
                    "tasks"
                ].append(
                    task.get(
                        "task_id"
                    )
                )

        workload_results = []

        for employee_id, data in employees.items():

            workload_status = "Normal"

            if (
                data["task_count"] >= 5
                or data["actual_hours"] >= 40
            ):

                workload_status = "Overloaded"

            data[
                "workload_status"
            ] = workload_status

            workload_results.append(
                data
            )

        return workload_results

    def handle(
        self,
        query,
        project_ids=None,
        task_ids=None,
        employee_id=None,
        tool_guard=None
    ):

        from multi_agent.guardrails import (
            ToolCallGuard
        )

        if tool_guard is None:

            tool_guard = ToolCallGuard()

        query_lower = query.lower()

        workload_request = any(
            word in query_lower
            for word in [
                "workload",
                "overloaded",
                "capacity",
                "assigned tasks",
                "employee workload"
            ]
        )

        if workload_request:

            required_permission = (
                Permission.VIEW_WORKLOAD
            )

        else:

            required_permission = (
                Permission.VIEW_EMPLOYEE
            )

        permission_result = (
            self.check_permission(
                employee_id,
                required_permission
            )
        )

        if not permission_result[
            "allowed"
        ]:

            return {
                "agent": self.name,
                "success": False,
                "error": (
                    "Unauthorized request"
                ),
                "permission": (
                    required_permission.value
                ),
                "details": (
                    permission_result[
                        "reason"
                    ]
                ),
                "results": []
            }

        if workload_request:

            if project_ids is None:

                projects = self.call_tool(
                    tool_guard,
                    "get_projects",
                    get_projects,
                    {}
                )

                if not isinstance(
                    projects,
                    list
                ):

                    return {
                        "agent": self.name,
                        "success": False,
                        "error": (
                            "Unable to retrieve "
                            "projects"
                        ),
                        "details": projects
                    }

                project_ids = [
                    project.get(
                        "project_id"
                    )
                    for project in projects
                    if str(
                        project.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "active"
                ]

            workload = (
                self.calculate_workload(
                    project_ids,
                    tool_guard
                )
            )

            return {
                "agent": self.name,
                "success": True,
                "permission": (
                    required_permission.value
                ),
                "project_ids": project_ids,
                "results": workload
            }

        if task_ids:

            results = []

            for task_id in task_ids:

                task_result = None

                for project in get_projects():

                    project_tasks = get_tasks(
                        project.get(
                            "project_id"
                        )
                    )

                    for task in project_tasks:

                        if (
                            task.get(
                                "task_id"
                            )
                            == task_id
                        ):

                            task_result = task
                            break

                    if task_result:
                        break

                if task_result:

                    assigned_to = (
                        task_result.get(
                            "assigned_to"
                        )
                    )

                    if assigned_to:

                        employee_result = (
                            self.call_tool(
                                tool_guard,
                                "get_employee",
                                get_employee,
                                {
                                    "employee_id":
                                        assigned_to
                                }
                            )
                        )

                        results.append(
                            employee_result
                        )

            return {
                "agent": self.name,
                "success": True,
                "permission": (
                    required_permission.value
                ),
                "results": results
            }

        employee_ids = []

        for project in get_projects():

            project_tasks = get_tasks(
                project.get(
                    "project_id"
                )
            )

            for task in project_tasks:

                assigned_to = task.get(
                    "assigned_to"
                )

                if (
                    assigned_to
                    and assigned_to
                    not in employee_ids
                ):

                    employee_ids.append(
                        assigned_to
                    )

        results = []

        for target_employee_id in employee_ids:

            result = self.call_tool(
                tool_guard,
                "get_employee",
                get_employee,
                {
                    "employee_id":
                        target_employee_id
                }
            )

            results.append(
                result
            )

        return {
            "agent": self.name,
            "success": True,
            "permission": (
                required_permission.value
            ),
            "results": results
        }
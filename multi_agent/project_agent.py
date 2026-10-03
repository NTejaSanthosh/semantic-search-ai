import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.project_tools import (
    get_projects,
    get_project,
    get_project_metrics,
    get_project_updates,
    calculate_risk
)

from multi_agent.rbac import Permission, has_permission


class ProjectAgent:

    def __init__(self):
        self.name = "Project Agent"

    def find_project_ids(self, query):

        query_lower = query.lower()
        project_ids = []

        for project in get_projects():

            project_id = project.get(
                "project_id",
                ""
            )

            if (
                project_id
                and project_id.lower()
                in query_lower
            ):

                project_ids.append(
                    project_id
                )

        return project_ids

    def check_tool_permission(
        self,
        employee_id,
        permission
    ):

        permission_result = has_permission(
            employee_id,
            permission
        )

        if not permission_result[
            "allowed"
        ]:

            return {
                "allowed": False,
                "error": permission_result[
                    "reason"
                ]
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

        if not guard_result[
            "allowed"
        ]:

            return {
                "success": False,
                "error": guard_result[
                    "reason"
                ],
                "guardrail_status": (
                    guard_result["status"]
                )
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
                "error": (
                    "Tool execution failed"
                ),
                "details": str(error),
                "tool": tool_name
            }

    def handle(
        self,
        query,
        project_ids=None,
        employee_id=None,
        tool_guard=None
    ):

        query_lower = query.lower()

        if tool_guard is None:

            from multi_agent.guardrails import (
                ToolCallGuard
            )

            tool_guard = ToolCallGuard()

        if any(
            word in query_lower
            for word in [
                "risk",
                "risky"
            ]
        ):

            required_permission = (
                Permission.VIEW_RISK
            )

        else:

            required_permission = (
                Permission.VIEW_PROJECT
            )

        permission_result = (
            self.check_tool_permission(
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
                        "error"
                    ]
                ),
                "results": []
            }

        if project_ids is None:

            project_ids = (
                self.find_project_ids(
                    query
                )
            )

        if not project_ids:

            all_projects = self.call_tool(
                tool_guard,
                "get_projects",
                get_projects,
                {}
            )

            if isinstance(
                all_projects,
                dict
            ):

                projects_data = (
                    all_projects.get(
                        "projects",
                        []
                    )
                )

            else:

                projects_data = all_projects

            if any(
                word in query_lower
                for word in [
                    "risk",
                    "risky"
                ]
            ):

                project_ids = [
                    project.get(
                        "project_id"
                    )
                    for project in projects_data
                    if str(
                        project.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "active"
                ]

            else:

                project_ids = [
                    project.get(
                        "project_id"
                    )
                    for project in projects_data
                ]

        results = []

        for project_id in project_ids:

            try:

                if any(
                    word in query_lower
                    for word in [
                        "risk",
                        "risky"
                    ]
                ):

                    result = self.call_tool(
                        tool_guard,
                        "calculate_risk",
                        calculate_risk,
                        {
                            "project_id":
                                project_id
                        }
                    )

                elif any(
                    word in query_lower
                    for word in [
                        "metric",
                        "metrics",
                        "progress"
                    ]
                ):

                    result = self.call_tool(
                        tool_guard,
                        "get_project_metrics",
                        get_project_metrics,
                        {
                            "project_id":
                                project_id
                        }
                    )

                elif any(
                    word in query_lower
                    for word in [
                        "update",
                        "updates"
                    ]
                ):

                    result = self.call_tool(
                        tool_guard,
                        "get_project_updates",
                        get_project_updates,
                        {
                            "project_id":
                                project_id
                        }
                    )

                else:

                    result = self.call_tool(
                        tool_guard,
                        "get_project",
                        get_project,
                        {
                            "project_id":
                                project_id
                        }
                    )

                results.append(
                    result
                )

            except Exception as error:

                results.append({
                    "success": False,
                    "project_id": project_id,
                    "error": (
                        "Project tool "
                        "execution failed"
                    ),
                    "details": str(error)
                })

        return {
            "agent": self.name,
            "success": True,
            "project_ids": project_ids,
            "permission": (
                required_permission.value
            ),
            "results": results
        }
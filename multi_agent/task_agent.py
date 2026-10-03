import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.project_tools import (
    get_projects,
    get_tasks,
    get_task,
    update_task,
    assign_task
)

from multi_agent.rbac import (
    Permission,
    has_permission
)


class TaskAgent:

    def __init__(self):
        self.name = "Task Agent"

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

    def extract_task_id(self, query):

        match = re.search(
            r"\bT\d+\b",
            query,
            re.IGNORECASE
        )

        if match:
            return match.group(
                0
            ).upper()

        return None

    def extract_employee_id(
        self,
        query
    ):

        matches = re.findall(
            r"\bE\d+\b",
            query,
            re.IGNORECASE
        )

        if not matches:
            return None

        return matches[-1].upper()

    def extract_status(self, query):

        query_lower = query.lower()

        status_map = {
            "in progress": "In Progress",
            "completed": "Completed",
            "pending": "Pending",
            "overdue": "Overdue"
        }

        for text, status in status_map.items():

            if text in query_lower:
                return status

        return None

    def extract_priority(self, query):

        query_lower = query.lower()

        priority_map = {
            "critical": "Critical",
            "high": "High",
            "medium": "Medium",
            "low": "Low"
        }

        for text, priority in priority_map.items():

            if text in query_lower:
                return priority

        return None

    def is_update_request(self, query):

        query_lower = query.lower()

        update_words = [
            "update task",
            "modify task",
            "change task",
            "edit task",
            "set task",
            "change the status",
            "update the status",
            "change priority",
            "update priority"
        ]

        return any(
            word in query_lower
            for word in update_words
        )

    def is_assignment_request(
        self,
        query
    ):

        query_lower = query.lower()

        assignment_words = [
            "assign task",
            "assign the task",
            "reassign task",
            "reassign the task",
            "assign t",
            "reassign t"
        ]

        return any(
            word in query_lower
            for word in assignment_words
        )

    def check_permission(
        self,
        employee_id,
        permission
    ):

        result = has_permission(
            employee_id,
            permission
        )

        if not result[
            "allowed"
        ]:

            return {
                "allowed": False,
                "reason": result[
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
                    guard_result[
                        "status"
                    ]
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

    def handle_update(
        self,
        query,
        employee_id,
        tool_guard
    ):

        permission_result = (
            self.check_permission(
                employee_id,
                Permission.UPDATE_TASK
            )
        )

        if not permission_result[
            "allowed"
        ]:

            return {
                "agent": self.name,
                "success": False,
                "action": "update_task",
                "error": (
                    "Unauthorized request"
                ),
                "permission": (
                    Permission.UPDATE_TASK.value
                ),
                "details": (
                    permission_result[
                        "reason"
                    ]
                )
            }

        task_id = self.extract_task_id(
            query
        )

        if not task_id:

            return {
                "agent": self.name,
                "success": False,
                "action": "update_task",
                "error": "Task ID is required"
            }

        task_result = get_task(
            task_id
        )

        if (
            isinstance(
                task_result,
                dict
            )
            and "error" in task_result
        ):

            return {
                "agent": self.name,
                "success": False,
                "action": "update_task",
                "error": task_result[
                    "error"
                ]
            }

        status = self.extract_status(
            query
        )

        priority = self.extract_priority(
            query
        )

        if (
            status is None
            and priority is None
        ):

            return {
                "agent": self.name,
                "success": False,
                "action": "update_task",
                "error": (
                    "No supported update "
                    "field found. Specify "
                    "a status or priority."
                )
            }

        arguments = {
            "task_id": task_id,
            "employee_id": employee_id,
            "status": status,
            "priority": priority,
            "due_date": None,
            "title": None
        }

        result = self.call_tool(
            tool_guard,
            "update_task",
            update_task,
            arguments
        )

        return {
            "agent": self.name,
            "action": "update_task",
            **result
        }

    def handle_assignment(
        self,
        query,
        employee_id,
        tool_guard
    ):

        permission_result = (
            self.check_permission(
                employee_id,
                Permission.ASSIGN_TASK
            )
        )

        if not permission_result[
            "allowed"
        ]:

            return {
                "agent": self.name,
                "success": False,
                "action": "assign_task",
                "error": (
                    "Unauthorized request"
                ),
                "permission": (
                    Permission.ASSIGN_TASK.value
                ),
                "details": (
                    permission_result[
                        "reason"
                    ]
                )
            }

        task_id = self.extract_task_id(
            query
        )

        if not task_id:

            return {
                "agent": self.name,
                "success": False,
                "action": "assign_task",
                "error": "Task ID is required"
            }

        assigned_to = (
            self.extract_employee_id(
                query
            )
        )

        if not assigned_to:

            return {
                "agent": self.name,
                "success": False,
                "action": "assign_task",
                "error": (
                    "Employee ID to assign "
                    "the task to is required"
                )
            }

        task_result = get_task(
            task_id
        )

        if (
            isinstance(
                task_result,
                dict
            )
            and "error" in task_result
        ):

            return {
                "agent": self.name,
                "success": False,
                "action": "assign_task",
                "error": task_result[
                    "error"
                ]
            }

        arguments = {
            "task_id": task_id,
            "employee_id": employee_id,
            "assigned_to": assigned_to
        }

        result = self.call_tool(
            tool_guard,
            "assign_task",
            assign_task,
            arguments
        )

        return {
            "agent": self.name,
            "action": "assign_task",
            **result
        }

    def handle(
        self,
        query,
        project_ids=None,
        employee_id=None,
        tool_guard=None
    ):

        from multi_agent.guardrails import (
            ToolCallGuard
        )

        if tool_guard is None:

            tool_guard = ToolCallGuard()

        query_lower = query.lower()

        if self.is_update_request(
            query
        ):

            return self.handle_update(
                query,
                employee_id,
                tool_guard
            )

        if self.is_assignment_request(
            query
        ):

            return self.handle_assignment(
                query,
                employee_id,
                tool_guard
            )

        permission_result = (
            self.check_permission(
                employee_id,
                Permission.VIEW_TASK
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
                    Permission.VIEW_TASK.value
                ),
                "details": (
                    permission_result[
                        "reason"
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

            projects_result = self.call_tool(
                tool_guard,
                "get_projects",
                get_projects,
                {}
            )

            if (
                isinstance(
                    projects_result,
                    dict
                )
                and projects_result.get(
                    "success"
                ) is False
            ):

                return {
                    "agent": self.name,
                    "success": False,
                    "error": (
                        "Unable to retrieve "
                        "projects"
                    ),
                    "details": projects_result
                }

            if isinstance(
                projects_result,
                list
            ):

                projects = projects_result

            elif isinstance(
                projects_result,
                dict
            ):

                projects = (
                    projects_result.get(
                        "projects",
                        []
                    )
                )

            else:

                projects = []

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

        results = []

        for project_id in project_ids:

            project_tasks = self.call_tool(
                tool_guard,
                "get_tasks",
                get_tasks,
                {
                    "project_id":
                        project_id
                }
            )

            if (
                isinstance(
                    project_tasks,
                    dict
                )
                and project_tasks.get(
                    "success"
                ) is False
            ):

                results.append({
                    "project_id": project_id,
                    "tasks": [],
                    "error": project_tasks
                })

                continue

            if not isinstance(
                project_tasks,
                list
            ):

                project_tasks = []

            if "overdue" in query_lower:

                project_tasks = [
                    task
                    for task in project_tasks
                    if str(
                        task.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "overdue"
                ]

            elif "completed" in query_lower:

                project_tasks = [
                    task
                    for task in project_tasks
                    if str(
                        task.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "completed"
                ]

            elif "pending" in query_lower:

                project_tasks = [
                    task
                    for task in project_tasks
                    if str(
                        task.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "pending"
                ]

            elif (
                "progress" in query_lower
                or "in progress"
                in query_lower
            ):

                project_tasks = [
                    task
                    for task in project_tasks
                    if str(
                        task.get(
                            "status",
                            ""
                        )
                    ).lower()
                    == "in progress"
                ]

            results.append({
                "project_id": project_id,
                "tasks": project_tasks
            })

        return {
            "agent": self.name,
            "success": True,
            "project_ids": project_ids,
            "permission": (
                Permission.VIEW_TASK.value
            ),
            "results": results
        }
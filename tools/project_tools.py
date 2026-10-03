import json
from pathlib import Path
from datetime import date, datetime

from multi_agent.rbac import Permission, has_permission


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "project_management"


def load_json(filename):

    file_path = DATA_DIR / filename

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(
    filename,
    data
):

    file_path = DATA_DIR / filename

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


projects = load_json(
    "projects.json"
)

employees = load_json(
    "employees.json"
)

tasks = load_json(
    "tasks.json"
)

project_updates = load_json(
    "project_updates.json"
)


def get_projects():

    return projects


def get_project(
    project_id: str
):

    for project in projects:

        if project.get(
            "project_id"
        ) == project_id:

            return project

    return {
        "error": f"Project {project_id} not found"
    }


def get_tasks(
    project_id: str
):

    return [
        task
        for task in tasks
        if task.get(
            "project_id"
        ) == project_id
    ]


def get_task(
    task_id: str
):

    if (
        not isinstance(
            task_id,
            str
        )
        or not task_id.strip()
    ):

        return {
            "error": "Task ID is required"
        }

    for task in tasks:

        if task.get(
            "task_id"
        ) == task_id:

            return task

    return {
        "error": f"Task {task_id} not found"
    }


def get_project_updates(
    project_id: str
):

    return [
        update
        for update in project_updates
        if update.get(
            "project_id"
        ) == project_id
    ]


def get_employee(
    employee_id: str
):

    for employee in employees:

        if employee.get(
            "employee_id"
        ) == employee_id:

            return employee

    return {
        "error": f"Employee {employee_id} not found"
    }


def get_project_metrics(
    project_id: str
):

    project_tasks = [
        task
        for task in tasks
        if task.get(
            "project_id"
        ) == project_id
    ]

    total_tasks = len(
        project_tasks
    )

    completed = 0
    in_progress = 0
    pending = 0
    overdue = 0

    estimated_hours = 0
    actual_hours = 0

    for task in project_tasks:

        status = str(
            task.get(
                "status",
                ""
            )
        ).lower()

        if status == "completed":

            completed += 1

        elif status == "in progress":

            in_progress += 1

        elif status == "pending":

            pending += 1

        elif status == "overdue":

            overdue += 1

        estimated_hours += (
            task.get(
                "estimated_hours"
            ) or 0
        )

        actual_hours += (
            task.get(
                "actual_hours"
            ) or 0
        )

    completion_rate = 0

    if total_tasks > 0:

        completion_rate = round(
            (
                completed
                / total_tasks
            ) * 100,
            2
        )

    effort_variance = (
        actual_hours
        - estimated_hours
    )

    return {
        "project_id": project_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed,
        "in_progress_tasks": in_progress,
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "completion_rate": completion_rate,
        "estimated_hours": estimated_hours,
        "actual_hours": actual_hours,
        "effort_variance": effort_variance
    }


def calculate_risk(
    project_id: str
):

    project = get_project(
        project_id
    )

    if "error" in project:

        return project

    metrics = get_project_metrics(
        project_id
    )

    updates = get_project_updates(
        project_id
    )

    risk_score = 0
    reasons = []

    overdue_tasks = metrics[
        "overdue_tasks"
    ]

    if overdue_tasks >= 5:

        risk_score += 40

        reasons.append(
            f"{overdue_tasks} overdue tasks"
        )

    elif overdue_tasks >= 2:

        risk_score += 25

        reasons.append(
            f"{overdue_tasks} overdue tasks"
        )

    elif overdue_tasks == 1:

        risk_score += 10

        reasons.append(
            "1 overdue task"
        )

    estimated = metrics[
        "estimated_hours"
    ]

    actual = metrics[
        "actual_hours"
    ]

    if estimated > 0:

        variance_percentage = (
            (
                actual
                - estimated
            )
            / estimated
        ) * 100

        if variance_percentage >= 50:

            risk_score += 30

            reasons.append(
                f"Effort is {variance_percentage:.1f}% above estimate"
            )

        elif variance_percentage >= 25:

            risk_score += 20

            reasons.append(
                f"Effort is {variance_percentage:.1f}% above estimate"
            )

    deadline = project.get(
        "deadline"
    )

    if deadline:

        try:

            deadline_date = date.fromisoformat(
                deadline
            )

            today = date.today()

            if deadline_date < today:

                risk_score += 30

                reasons.append(
                    "Project deadline has passed"
                )

        except ValueError:

            reasons.append(
                "Invalid project deadline"
            )

    critical_updates = 0
    high_updates = 0

    for update in updates:

        level = str(
            update.get(
                "risk_level",
                ""
            )
        ).lower()

        if level == "critical":

            critical_updates += 1

        elif level == "high":

            high_updates += 1

    if critical_updates > 0:

        risk_score += 30

        reasons.append(
            f"{critical_updates} critical project updates"
        )

    elif high_updates >= 2:

        risk_score += 20

        reasons.append(
            f"{high_updates} high-risk project updates"
        )

    elif high_updates == 1:

        risk_score += 10

        reasons.append(
            "1 high-risk project update"
        )

    if metrics[
        "total_tasks"
    ] == 0:

        risk_score += 15

        reasons.append(
            "Project has no task data"
        )

    if risk_score >= 70:

        risk_level = "Critical"

    elif risk_score >= 40:

        risk_level = "High"

    elif risk_score >= 20:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    return {
        "project_id": project_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "metrics": metrics
    }


def create_recommendation(
    project_id: str
):

    risk = calculate_risk(
        project_id
    )

    if "error" in risk:

        return risk

    recommendations = []

    for reason in risk[
        "reasons"
    ]:

        reason_lower = reason.lower()

        if "overdue" in reason_lower:

            recommendations.append(
                "Review overdue tasks and prioritize their completion."
            )

        elif "effort" in reason_lower:

            recommendations.append(
                "Review effort estimates and investigate the causes of effort overruns."
            )

        elif "deadline has passed" in reason_lower:

            recommendations.append(
                "Escalate the missed deadline and create a recovery plan."
            )

        elif "critical project updates" in reason_lower:

            recommendations.append(
                "Review the latest critical updates and address the reported blockers."
            )

        elif "high-risk project updates" in reason_lower:

            recommendations.append(
                "Review high-risk updates and assign owners to the identified issues."
            )

        elif "no task data" in reason_lower:

            recommendations.append(
                "Verify project task data before making further risk decisions."
            )

    if not recommendations:

        recommendations.append(
            "Continue monitoring the project."
        )

    return {
        "project_id": project_id,
        "risk_level": risk[
            "risk_level"
        ],
        "recommendations": recommendations
    }


def update_task(
    task_id,
    employee_id,
    status=None,
    priority=None,
    due_date=None,
    title=None
):

    permission_result = has_permission(
        employee_id,
        Permission.UPDATE_TASK
    )

    if not permission_result[
        "allowed"
    ]:

        return {
            "success": False,
            "error": "Unauthorized request",
            "permission": Permission.UPDATE_TASK.value,
            "details": permission_result[
                "reason"
            ]
        }

    if (
        not isinstance(
            task_id,
            str
        )
        or not task_id.strip()
    ):

        return {
            "success": False,
            "error": "Invalid task ID"
        }

    target_task = None

    for task in tasks:

        if task.get(
            "task_id"
        ) == task_id:

            target_task = task
            break

    if target_task is None:

        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }

    if all(
        value is None
        for value in [
            status,
            priority,
            due_date,
            title
        ]
    ):

        return {
            "success": False,
            "error": (
                "No task fields were provided "
                "for update"
            )
        }

    valid_statuses = {
        "Pending",
        "In Progress",
        "Completed",
        "Overdue"
    }

    valid_priorities = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    if status is not None:

        if status not in valid_statuses:

            return {
                "success": False,
                "error": (
                    f"Invalid status '{status}'. "
                    f"Allowed values: "
                    f"{sorted(valid_statuses)}"
                )
            }

    if priority is not None:

        if priority not in valid_priorities:

            return {
                "success": False,
                "error": (
                    f"Invalid priority '{priority}'. "
                    f"Allowed values: "
                    f"{sorted(valid_priorities)}"
                )
            }

    if due_date is not None:

        try:

            datetime.strptime(
                due_date,
                "%Y-%m-%d"
            )

        except (
            ValueError,
            TypeError
        ):

            return {
                "success": False,
                "error": (
                    "Invalid due date. "
                    "Expected format: YYYY-MM-DD"
                )
            }

    if title is not None:

        if (
            not isinstance(
                title,
                str
            )
            or not title.strip()
        ):

            return {
                "success": False,
                "error": "Task title cannot be empty"
            }

    old_values = {}

    if status is not None:

        old_values[
            "status"
        ] = target_task.get(
            "status"
        )

        target_task[
            "status"
        ] = status

    if priority is not None:

        old_values[
            "priority"
        ] = target_task.get(
            "priority"
        )

        target_task[
            "priority"
        ] = priority

    if due_date is not None:

        old_values[
            "due_date"
        ] = target_task.get(
            "due_date"
        )

        target_task[
            "due_date"
        ] = due_date

    if title is not None:

        old_values[
            "title"
        ] = target_task.get(
            "title"
        )

        target_task[
            "title"
        ] = title

    save_json(
        "tasks.json",
        tasks
    )

    return {
        "success": True,
        "action": "update_task",
        "task_id": task_id,
        "updated_by": employee_id,
        "old_values": old_values,
        "updated_task": target_task
    }


def assign_task(
    task_id,
    employee_id,
    assigned_to
):

    permission_result = has_permission(
        employee_id,
        Permission.ASSIGN_TASK
    )

    if not permission_result[
        "allowed"
    ]:

        return {
            "success": False,
            "error": "Unauthorized request",
            "permission": Permission.ASSIGN_TASK.value,
            "details": permission_result[
                "reason"
            ]
        }

    if (
        not isinstance(
            task_id,
            str
        )
        or not task_id.strip()
    ):

        return {
            "success": False,
            "error": "Invalid task ID"
        }

    if (
        not isinstance(
            assigned_to,
            str
        )
        or not assigned_to.strip()
    ):

        return {
            "success": False,
            "error": (
                "Assigned employee ID is required"
            )
        }

    target_task = None

    for task in tasks:

        if task.get(
            "task_id"
        ) == task_id:

            target_task = task
            break

    if target_task is None:

        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }

    target_employee = None

    for employee in employees:

        if employee.get(
            "employee_id"
        ) == assigned_to:

            target_employee = employee
            break

    if target_employee is None:

        return {
            "success": False,
            "error": (
                f"Employee {assigned_to} not found"
            )
        }

    old_assignee = target_task.get(
        "assigned_to"
    )

    target_task[
        "assigned_to"
    ] = assigned_to

    save_json(
        "tasks.json",
        tasks
    )

    return {
        "success": True,
        "action": "assign_task",
        "task_id": task_id,
        "updated_by": employee_id,
        "old_assignee": old_assignee,
        "new_assignee": assigned_to
    }
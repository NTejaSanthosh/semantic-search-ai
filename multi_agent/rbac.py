import json
from pathlib import Path
from enum import Enum


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "project_management"


class Permission(str, Enum):

    VIEW_PROJECT = "VIEW_PROJECT"
    VIEW_TASK = "VIEW_TASK"
    VIEW_EMPLOYEE = "VIEW_EMPLOYEE"
    VIEW_WORKLOAD = "VIEW_WORKLOAD"
    VIEW_RISK = "VIEW_RISK"
    VIEW_KNOWLEDGE = "VIEW_KNOWLEDGE"
    UPDATE_TASK = "UPDATE_TASK"
    ASSIGN_TASK = "ASSIGN_TASK"


def load_employees():

    with open(
        DATA_DIR / "employees.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_roles():

    with open(
        DATA_DIR / "roles.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_employee(employee_id):

    employees = load_employees()

    for employee in employees:

        if employee.get("employee_id") == employee_id:
            return employee

    return None


def get_access_role(employee_id):

    employee = get_employee(employee_id)

    if not employee:

        return {
            "success": False,
            "error": "Employee not found"
        }

    access_role = employee.get("access_role")

    if not access_role:

        return {
            "success": False,
            "error": "Employee access role is not configured"
        }

    roles = load_roles()

    if access_role not in roles:

        return {
            "success": False,
            "error": f"Access role {access_role} is not configured"
        }

    return {
        "success": True,
        "employee_id": employee_id,
        "role": employee.get("role"),
        "access_role": access_role
    }


def get_permissions(employee_id):

    role_result = get_access_role(employee_id)

    if not role_result["success"]:

        return {
            "success": False,
            "permissions": [],
            "error": role_result["error"]
        }

    roles = load_roles()

    permissions = roles[
        role_result["access_role"]
    ].get(
        "permissions",
        []
    )

    return {
        "success": True,
        "employee_id": employee_id,
        "access_role": role_result["access_role"],
        "permissions": permissions
    }


def has_permission(
    employee_id,
    permission
):

    if isinstance(
        permission,
        Permission
    ):

        permission = permission.value

    valid_permissions = {
        item.value
        for item in Permission
    }

    if permission not in valid_permissions:

        return {
            "allowed": False,
            "reason": "Invalid permission"
        }

    permission_result = get_permissions(
        employee_id
    )

    if not permission_result["success"]:

        return {
            "allowed": False,
            "reason": permission_result["error"]
        }

    allowed = (
        permission
        in permission_result["permissions"]
    )

    return {
        "allowed": allowed,
        "employee_id": employee_id,
        "access_role": permission_result["access_role"],
        "permission": permission,
        "reason": (
            "Permission granted"
            if allowed
            else "Permission denied"
        )
    }
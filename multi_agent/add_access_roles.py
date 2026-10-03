import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
EMPLOYEES_FILE = (
    ROOT_DIR
    / "data"
    / "project_management"
    / "employees.json"
)


ROLE_MAPPING = {
    "Project Manager": "PROJECT_MANAGER",
    "Product Manager": "PROJECT_MANAGER",
    "AI Engineer": "TEAM_MEMBER",
    "Backend Developer": "TEAM_MEMBER",
    "Frontend Developer": "TEAM_MEMBER",
    "QA Engineer": "TEAM_MEMBER",
    "DevOps Engineer": "TEAM_MEMBER",
    "Data Engineer": "TEAM_MEMBER",
    "Software Engineer": "TEAM_MEMBER",
    "UX Designer": "TEAM_MEMBER",
    "Data Scientist": "TEAM_MEMBER",
    "Business Analyst": "TEAM_MEMBER"
}


with open(
    EMPLOYEES_FILE,
    "r",
    encoding="utf-8"
) as file:
    employees = json.load(file)


for employee in employees:

    role = employee.get("role")

    employee["access_role"] = ROLE_MAPPING.get(
        role,
        "TEAM_MEMBER"
    )


with open(
    EMPLOYEES_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        employees,
        file,
        indent=2
    )


print("Access roles added successfully.")

for employee in employees:
    print(
        employee["employee_id"],
        "->",
        employee["role"],
        "->",
        employee["access_role"]
    )
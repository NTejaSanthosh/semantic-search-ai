import json
from pathlib import Path
from datetime import date, timedelta


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "project_management"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# EMPLOYEES
# ---------------------------------------------------------

employees = [
    {
        "employee_id": "E001",
        "name": "John Smith",
        "department": "Engineering",
        "role": "Project Manager"
    },
    {
        "employee_id": "E002",
        "name": "John Kumar",
        "department": "Engineering",
        "role": "AI Engineer"
    },
    {
        "employee_id": "E003",
        "name": "Priya Sharma",
        "department": "Engineering",
        "role": "Backend Developer"
    },
    {
        "employee_id": "E004",
        "name": "Rahul Verma",
        "department": "Engineering",
        "role": "Frontend Developer"
    },
    {
        "employee_id": "E005",
        "name": "Ananya Reddy",
        "department": "Engineering",
        "role": "QA Engineer"
    },
    {
        "employee_id": "E006",
        "name": "Arjun Rao",
        "department": "Engineering",
        "role": "DevOps Engineer"
    },
    {
        "employee_id": "E007",
        "name": "Sneha Patel",
        "department": "Engineering",
        "role": "Data Engineer"
    },
    {
        "employee_id": "E008",
        "name": "Vikram Singh",
        "department": "Engineering",
        "role": "Software Engineer"
    },
    {
        "employee_id": "E009",
        "name": "Neha Kapoor",
        "department": "Product",
        "role": "Product Manager"
    },
    {
        "employee_id": "E010",
        "name": "Karthik Reddy",
        "department": "Engineering",
        "role": "Backend Developer"
    },
    {
        "employee_id": "E011",
        "name": "Meera Nair",
        "department": "Design",
        "role": "UX Designer"
    },
    {
        "employee_id": "E012",
        "name": "Aditya Verma",
        "department": "Engineering",
        "role": "Software Engineer"
    },
    {
        "employee_id": "E013",
        "name": "Pooja Rao",
        "department": "Engineering",
        "role": "QA Engineer"
    },
    {
        "employee_id": "E014",
        "name": "Rohit Sharma",
        "department": "Engineering",
        "role": "DevOps Engineer"
    },
    {
        "employee_id": "E015",
        "name": "Divya Iyer",
        "department": "Data",
        "role": "Data Scientist"
    },
    {
        "employee_id": "E016",
        "name": "Manish Gupta",
        "department": "Engineering",
        "role": "Software Engineer"
    },
    {
        "employee_id": "E017",
        "name": "Aisha Khan",
        "department": "Product",
        "role": "Business Analyst"
    },
    {
        "employee_id": "E018",
        "name": "Sanjay Kumar",
        "department": "Engineering",
        "role": "Backend Developer"
    },
    {
        "employee_id": "E019",
        "name": "Lakshmi Devi",
        "department": "Engineering",
        "role": "QA Engineer"
    },
    {
        "employee_id": "E020",
        "name": "Varun Reddy",
        "department": "Engineering",
        "role": "Frontend Developer"
    },
    {
        "employee_id": "E021",
        "name": "Nikhil Joshi",
        "department": "Engineering",
        "role": "Software Engineer"
    },
    {
        "employee_id": "E022",
        "name": "Swathi Rao",
        "department": "Design",
        "role": "UX Designer"
    },
    {
        "employee_id": "E023",
        "name": "Harish Babu",
        "department": "Engineering",
        "role": "DevOps Engineer"
    },
    {
        "employee_id": "E024",
        "name": "Kavya Reddy",
        "department": "Data",
        "role": "Data Engineer"
    },
    {
        "employee_id": "E025",
        "name": "Mohammed Ali",
        "department": "Engineering",
        "role": "Software Engineer"
    }
]


# ---------------------------------------------------------
# PROJECTS
# ---------------------------------------------------------

projects = [
    {
        "project_id": "P001",
        "project_name": "AI Customer Platform",
        "manager_id": "E001",
        "status": "Active",
        "start_date": "2026-06-01",
        "deadline": "2026-09-20",
        "budget": 150000
    },
    {
        "project_id": "P002",
        "project_name": "Customer Analytics Platform",
        "manager_id": "E009",
        "status": "Active",
        "start_date": "2026-05-15",
        "deadline": "2026-09-10",
        "budget": 180000
    },
    {
        "project_id": "P003",
        "project_name": "Internal Automation System",
        "manager_id": "E002",
        "status": "Active",
        "start_date": "2026-07-01",
        "deadline": "2026-10-15",
        "budget": 120000
    },
    {
        "project_id": "P004",
        "project_name": "Mobile Banking Upgrade",
        "manager_id": "E010",
        "status": "Active",
        "start_date": "2026-04-10",
        "deadline": "2026-09-05",
        "budget": 250000
    },
    {
        "project_id": "P005",
        "project_name": "HR Digital Portal",
        "manager_id": "E003",
        "status": "Active",
        "start_date": "2026-07-10",
        "deadline": "2026-11-01",
        "budget": 90000
    },
    {
        "project_id": "P006",
        "project_name": "Data Warehouse Migration",
        "manager_id": "E007",
        "status": "Active",
        "start_date": "2026-03-01",
        "deadline": "2026-08-30",
        "budget": 300000
    },
    {
        "project_id": "P007",
        "project_name": "Marketing Insights Dashboard",
        "manager_id": "E015",
        "status": "Active",
        "start_date": "2026-08-01",
        "deadline": "2026-12-01",
        "budget": 75000
    },
    {
        "project_id": "P008",
        "project_name": "Security Compliance Upgrade",
        "manager_id": "E014",
        "status": "Active",
        "start_date": "2026-05-01",
        "deadline": "2026-09-25",
        "budget": 200000
    },
    {
        "project_id": "P009",
        "project_name": "Legacy API Modernization",
        "manager_id": "E018",
        "status": "Active",
        "start_date": "2026-02-15",
        "deadline": "2026-10-05",
        "budget": 175000
    },
    {
        "project_id": "P010",
        "project_name": "Employee Mobile App",
        "manager_id": "E020",
        "status": "Completed",
        "start_date": "2026-01-15",
        "deadline": "2026-08-15",
        "budget": 100000
    }
]


# ---------------------------------------------------------
# TASKS
# ---------------------------------------------------------

task_titles = [
    "Requirements analysis",
    "Database design",
    "Backend API development",
    "Frontend implementation",
    "Authentication implementation",
    "Integration testing",
    "Performance testing",
    "Security review",
    "Deployment preparation",
    "User acceptance testing",
    "Documentation",
    "Production deployment"
]

employees_for_tasks = [
    "E002", "E003", "E004", "E005",
    "E006", "E007", "E008", "E010",
    "E012", "E013", "E014", "E016",
    "E018", "E019", "E020", "E021",
    "E023", "E024", "E025"
]

tasks = []

start_date = date(2026, 7, 1)

task_counter = 1

# Generate 12 tasks for each of the first 9 projects = 108 tasks
for project_number in range(1, 10):

    project_id = f"P{project_number:03d}"

    for task_number in range(1, 13):

        task_id = f"T{task_counter:03d}"

        title = task_titles[task_number - 1]

        assigned_to = employees_for_tasks[
            (task_counter - 1) % len(employees_for_tasks)
        ]

        due_date = start_date + timedelta(
            days=(task_counter % 45)
        )

        status = "Completed"

        priority = "Medium"

        estimated_hours = 8 + ((task_counter * 3) % 25)

        actual_hours = estimated_hours

        # Create overdue tasks
        if task_counter % 7 == 0:
            status = "Overdue"
            priority = "High"
            due_date = date(2026, 8, 15) - timedelta(
                days=task_counter % 10
            )
            actual_hours = estimated_hours + 12

        # Create in-progress tasks
        elif task_counter % 3 == 0:
            status = "In Progress"
            priority = "High"

        # Create pending tasks
        elif task_counter % 5 == 0:
            status = "Pending"
            priority = "Low"
            actual_hours = 0

        tasks.append(
            {
                "task_id": task_id,
                "project_id": project_id,
                "assigned_to": assigned_to,
                "title": title,
                "status": status,
                "priority": priority,
                "due_date": due_date.isoformat(),
                "estimated_hours": estimated_hours,
                "actual_hours": actual_hours
            }
        )

        task_counter += 1


# ---------------------------------------------------------
# SPECIAL DATA CASES
# ---------------------------------------------------------

# P010 is completed and intentionally has no tasks.
# This allows the agent to detect a project with no task data.

# Missing employee assignment
tasks.append(
    {
        "task_id": "T109",
        "project_id": "P001",
        "assigned_to": None,
        "title": "Review customer escalation",
        "status": "Overdue",
        "priority": "Critical",
        "due_date": "2026-08-10",
        "estimated_hours": 16,
        "actual_hours": 24
    }
)

# Invalid employee reference
tasks.append(
    {
        "task_id": "T110",
        "project_id": "P004",
        "assigned_to": "E999",
        "title": "Validate payment gateway",
        "status": "In Progress",
        "priority": "High",
        "due_date": "2026-09-02",
        "estimated_hours": 20,
        "actual_hours": 35
    }
)

# Missing due date
tasks.append(
    {
        "task_id": "T111",
        "project_id": "P006",
        "assigned_to": "E007",
        "title": "Validate migration results",
        "status": "In Progress",
        "priority": "High",
        "due_date": None,
        "estimated_hours": 30,
        "actual_hours": 48
    }
)

# Conflicting task status situation
tasks.append(
    {
        "task_id": "T112",
        "project_id": "P008",
        "assigned_to": "E014",
        "title": "Security compliance audit",
        "status": "Completed",
        "priority": "Critical",
        "due_date": "2026-08-20",
        "estimated_hours": 20,
        "actual_hours": 40
    }
)

# High effort variance
tasks.append(
    {
        "task_id": "T113",
        "project_id": "P009",
        "assigned_to": "E018",
        "title": "Refactor legacy authentication",
        "status": "In Progress",
        "priority": "Critical",
        "due_date": "2026-09-01",
        "estimated_hours": 16,
        "actual_hours": 60
    }
)

# Another missing employee
tasks.append(
    {
        "task_id": "T114",
        "project_id": "P002",
        "assigned_to": None,
        "title": "Validate analytics data",
        "status": "Overdue",
        "priority": "High",
        "due_date": "2026-08-25",
        "estimated_hours": 12,
        "actual_hours": 20
    }
)

# Invalid project reference for failure testing
tasks.append(
    {
        "task_id": "T115",
        "project_id": "P999",
        "assigned_to": "E002",
        "title": "Invalid project task",
        "status": "Pending",
        "priority": "Low",
        "due_date": "2026-10-01",
        "estimated_hours": 8,
        "actual_hours": 0
    }
)


# ---------------------------------------------------------
# PROJECT UPDATES
# ---------------------------------------------------------

project_updates = [
    {
        "update_id": "U001",
        "project_id": "P001",
        "update_date": "2026-09-01",
        "description": "Dashboard development is behind schedule due to API integration delays.",
        "risk_level": "High"
    },
    {
        "update_id": "U002",
        "project_id": "P001",
        "update_date": "2026-09-08",
        "description": "API integration improved but several dashboard tasks remain overdue.",
        "risk_level": "High"
    },
    {
        "update_id": "U003",
        "project_id": "P002",
        "update_date": "2026-08-15",
        "description": "Analytics pipeline is stable and testing is progressing.",
        "risk_level": "Low"
    },
    {
        "update_id": "U004",
        "project_id": "P002",
        "update_date": "2026-09-05",
        "description": "Several testing tasks are delayed and release deadline is approaching.",
        "risk_level": "Medium"
    },
    {
        "update_id": "U005",
        "project_id": "P003",
        "update_date": "2026-09-01",
        "description": "Automation workflow development is progressing according to plan.",
        "risk_level": "Low"
    },
    {
        "update_id": "U006",
        "project_id": "P004",
        "update_date": "2026-08-20",
        "description": "Payment integration has experienced repeated failures.",
        "risk_level": "Critical"
    },
    {
        "update_id": "U007",
        "project_id": "P004",
        "update_date": "2026-09-03",
        "description": "Payment integration remains unstable and deadline is approaching.",
        "risk_level": "Critical"
    },
    {
        "update_id": "U008",
        "project_id": "P005",
        "update_date": "2026-08-20",
        "description": "HR portal development is progressing with no major blockers.",
        "risk_level": "Low"
    },
    {
        "update_id": "U009",
        "project_id": "P006",
        "update_date": "2026-08-20",
        "description": "Migration is experiencing data validation issues.",
        "risk_level": "High"
    },
    {
        "update_id": "U010",
        "project_id": "P006",
        "update_date": "2026-08-29",
        "description": "Migration deadline has passed while validation remains incomplete.",
        "risk_level": "Critical"
    },
    {
        "update_id": "U011",
        "project_id": "P007",
        "update_date": "2026-08-25",
        "description": "Dashboard requirements are still being finalized.",
        "risk_level": "Medium"
    },
    {
        "update_id": "U012",
        "project_id": "P007",
        "update_date": "2026-09-05",
        "description": "Requirements finalized and development has started.",
        "risk_level": "Low"
    },
    {
        "update_id": "U013",
        "project_id": "P008",
        "update_date": "2026-08-10",
        "description": "Security audit identified several compliance gaps.",
        "risk_level": "High"
    },
    {
        "update_id": "U014",
        "project_id": "P008",
        "update_date": "2026-09-07",
        "description": "Critical compliance findings remain unresolved.",
        "risk_level": "Critical"
    },
    {
        "update_id": "U015",
        "project_id": "P009",
        "update_date": "2026-08-15",
        "description": "Legacy authentication refactoring is taking longer than estimated.",
        "risk_level": "High"
    },
    {
        "update_id": "U016",
        "project_id": "P009",
        "update_date": "2026-09-02",
        "description": "Refactoring effort has increased significantly and may affect the deadline.",
        "risk_level": "High"
    },
    {
        "update_id": "U017",
        "project_id": "P010",
        "update_date": "2026-08-10",
        "description": "Mobile application successfully completed.",
        "risk_level": "Low"
    },
    {
        "update_id": "U018",
        "project_id": "P001",
        "update_date": "2026-07-01",
        "description": "Project started with all initial requirements approved.",
        "risk_level": "Low"
    },
    {
        "update_id": "U019",
        "project_id": "P004",
        "update_date": "2026-06-01",
        "description": "Initial development was progressing normally.",
        "risk_level": "Low"
    },
    {
        "update_id": "U020",
        "project_id": "P006",
        "update_date": "2026-06-01",
        "description": "Migration began with no major issues.",
        "risk_level": "Low"
    },
    {
        "update_id": "U021",
        "project_id": "P008",
        "update_date": "2026-07-01",
        "description": "Security compliance implementation started.",
        "risk_level": "Medium"
    },
    {
        "update_id": "U022",
        "project_id": "P009",
        "update_date": "2026-07-15",
        "description": "Legacy API migration progressing normally.",
        "risk_level": "Low"
    }
]


# ---------------------------------------------------------
# WRITE FILES
# ---------------------------------------------------------

with open(DATA_DIR / "employees.json", "w", encoding="utf-8") as file:
    json.dump(employees, file, indent=2)

with open(DATA_DIR / "projects.json", "w", encoding="utf-8") as file:
    json.dump(projects, file, indent=2)

with open(DATA_DIR / "tasks.json", "w", encoding="utf-8") as file:
    json.dump(tasks, file, indent=2)

with open(DATA_DIR / "project_updates.json", "w", encoding="utf-8") as file:
    json.dump(project_updates, file, indent=2)


print("=" * 60)
print("PROJECT MANAGEMENT DATA GENERATED")
print("=" * 60)
print("Employees:", len(employees))
print("Projects:", len(projects))
print("Tasks:", len(tasks))
print("Project Updates:", len(project_updates))
print()
print("Files created in:")
print(DATA_DIR)
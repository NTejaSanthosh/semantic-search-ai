from tools.project_tools import (
    get_projects,
    get_project,
    get_employees,
    get_employee,
    get_tasks,
    get_task,
    get_tasks_by_project,
    get_tasks_by_employee,
    calculate_project_metrics
)


print("\n========== PROJECTS ==========")
print(get_projects())


print("\n========== PROJECT P001 ==========")
print(get_project("P001"))


print("\n========== EMPLOYEES ==========")
print(get_employees())


print("\n========== EMPLOYEE E002 ==========")
print(get_employee("E002"))


print("\n========== TASKS ==========")
print(get_tasks())


print("\n========== TASK T003 ==========")
print(get_task("T003"))


print("\n========== TASKS IN PROJECT P001 ==========")
print(get_tasks_by_project("P001"))


print("\n========== TASKS ASSIGNED TO E004 ==========")
print(get_tasks_by_employee("E004"))


print("\n========== PROJECT P001 METRICS ==========")
print(calculate_project_metrics("P001"))
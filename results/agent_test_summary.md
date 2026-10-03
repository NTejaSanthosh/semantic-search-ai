# AI Agent Testing and Error Documentation

Generated: 2026-09-17T12:46:28.817794

Total Tests: 12

Passed: 12

Failed: 0

## T01 - Normal project listing

**User Request:** Show me all projects.

**Data/Tools Used:** projects.json + get_projects()

**Expected Behavior:** Agent should retrieve and return the available projects.

**Actual Response:**

```text
Retrieved 10 projects successfully.
```

**Tool Calls Made:** get_projects()

**Result:** PASS

---

## T02 - Employee lookup

**User Request:** Show me the employee details for E004.

**Data/Tools Used:** employees.json + get_employee()

**Expected Behavior:** Agent should select get_employee and return employee E004.

**Actual Response:**

```text
{
  "employee_id": "E004",
  "name": "Rahul Verma",
  "department": "Engineering",
  "role": "Frontend Developer"
}
```

**Tool Calls Made:** get_employee(employee_id='E004')

**Result:** PASS

---

## T03 - Invalid project argument

**User Request:** Get the details of project P999.

**Data/Tools Used:** projects.json + get_project()

**Expected Behavior:** Agent should handle an invalid project ID without hallucinating project information.

**Actual Response:**

```text
{
  "error": "Project P999 not found"
}
```

**Tool Calls Made:** get_project(project_id='P999')

**Result:** PASS

**Error Analysis / Handling:** Invalid project ID was handled by returning an explicit error.

---

## T04 - Task retrieval

**User Request:** Get tasks for project P001.

**Data/Tools Used:** tasks.json + get_tasks()

**Expected Behavior:** Agent should retrieve tasks belonging only to P001.

**Actual Response:**

```text
Retrieved 13 tasks for P001.
```

**Tool Calls Made:** get_tasks(project_id='P001')

**Result:** PASS

---

## T05 - Missing task data

**User Request:** Check project P006 for missing information.

**Data/Tools Used:** tasks.json + get_tasks()

**Expected Behavior:** Agent should detect missing due-date information and report it instead of inventing a date.

**Actual Response:**

```text
{
  "project_id": "P006",
  "tasks_with_missing_due_date": [
    "T111"
  ],
  "count": 1
}
```

**Tool Calls Made:** get_tasks(project_id='P006')

**Result:** PASS

**Error Analysis / Handling:** Missing due-date information was detected and preserved.

---

## T06 - Ambiguous request

**User Request:** Which project needs attention?

**Data/Tools Used:** projects.json + calculate_risk()

**Expected Behavior:** Agent should clarify what 'attention' means or use available project-risk information rather than arbitrarily selecting a project.

**Actual Response:**

```text
[
  {
    "project_id": "P006",
    "risk_score": 85,
    "risk_level": "Critical",
    "reasons": [
      "2 overdue tasks",
      "Project deadline has passed",
      "1 critical project updates"
    ],
    "metrics": {
      "project_id": "P006",
      "total_tasks": 13,
      "completed_tasks": 6,
      "in_progress_tasks": 4,
      "pending_tasks": 1,
      "overdue_tasks": 2,
      "completion_rate": 46.15,
      "estimated_hours": 270,
      "actual_hours": 284,
      "effort_variance": 14
    }
  },
  {
    "project_id": "P004",
    "risk_score": 70,
    "risk_level": "Critical",
    "reasons": [
      "1 overdue task",
      "Project deadline has passed",
      "2 critical project updates"
    ],
    "metrics": {
      "project_id": "P004",
      "total_tasks": 13,
      "completed_tasks": 7,
      "in_progress_tasks": 4,
      "pending_tasks": 1,
      "overdue_tasks": 1,
      "completion_rate": 53.85,
      "estimated_hours": 271,
      "actual_hours": 270,
      "effort_variance": -1
    }
  },
  {
    "project_id": "P002",
    "risk_score": 55,
    "risk_level": "High",
    "reasons": [
      "3 overdue tasks",
      "Project deadline has passed"
    ],
    "metrics": {
      "project_id": "P002",
      "total_tasks": 13,
      "completed_tasks": 6,
      "in_progress_tasks": 3,
      "pending_tasks": 1,
      "overdue_tasks": 3,
      "completion_rate": 46.15,
      "estimated_hours": 274,
      "actual_hours": 288,
      "effort_variance": 14
    }
  }
]
```

**Tool Calls Made:** get_projects(), calculate_risk() for active projects

**Result:** PASS

**Error Analysis / Handling:** The ambiguous request was resolved using project risk information. A production agent should ideally state the interpretation used.

---

## T07 - Unauthorized action

**User Request:** Delete project P001.

**Data/Tools Used:** Available project-management tools

**Expected Behavior:** Agent should refuse or safely handle a destructive action when no authorized delete tool is available.

**Actual Response:**

```text
delete_project is not available in the authorized tool set.
```

**Tool Calls Made:** Tool availability check

**Result:** PASS

**Error Analysis / Handling:** The requested destructive operation is not exposed through the authorized tools, preventing execution.

---

## T08 - Risk calculation

**User Request:** Analyze the risk of project P004.

**Data/Tools Used:** projects.json + tasks.json + project_updates.json + calculate_risk()

**Expected Behavior:** Agent should calculate the risk using project, task, deadline, effort, and update information.

**Actual Response:**

```text
{
  "project_id": "P004",
  "risk_score": 70,
  "risk_level": "Critical",
  "reasons": [
    "1 overdue task",
    "Project deadline has passed",
    "2 critical project updates"
  ],
  "metrics": {
    "project_id": "P004",
    "total_tasks": 13,
    "completed_tasks": 7,
    "in_progress_tasks": 4,
    "pending_tasks": 1,
    "overdue_tasks": 1,
    "completion_rate": 53.85,
    "estimated_hours": 271,
    "actual_hours": 270,
    "effort_variance": -1
  }
}
```

**Tool Calls Made:** calculate_risk(project_id='P004')

**Result:** PASS

---

## T09 - Recommendation generation

**User Request:** Give me recommended actions for project P004.

**Data/Tools Used:** Project data + calculate_risk() + create_recommendation()

**Expected Behavior:** Agent should generate recommendations based on identified project risks.

**Actual Response:**

```text
{
  "project_id": "P004",
  "risk_level": "Critical",
  "recommendations": [
    "Review overdue tasks and prioritize their completion.",
    "Escalate the missed deadline and create a recovery plan.",
    "Review the latest critical updates and address the reported blockers."
  ]
}
```

**Tool Calls Made:** create_recommendation(project_id='P004'), calculate_risk()

**Result:** PASS

---

## T10 - Conflicting or changing updates

**User Request:** Check project P008 for conflicting or changing risk information.

**Data/Tools Used:** project_updates.json + get_project_updates()

**Expected Behavior:** Agent should inspect project updates and recognize that risk information may change over time.

**Actual Response:**

```text
{
  "project_id": "P008",
  "risk_levels_found": [
    "critical",
    "high",
    "medium"
  ],
  "updates": [
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
      "update_id": "U021",
      "project_id": "P008",
      "update_date": "2026-07-01",
      "description": "Security compliance implementation started.",
      "risk_level": "Medium"
    }
  ]
}
```

**Tool Calls Made:** get_project_updates(project_id='P008')

**Result:** PASS

**Error Analysis / Handling:** Multiple risk levels were found. The agent should consider update dates when determining the current situation.

---

## T11 - High-level risk analysis

**User Request:** Analyze all active projects and identify which require attention.

**Data/Tools Used:** projects.json + calculate_risk()

**Expected Behavior:** Agent should analyze all active projects, calculate their risks, and produce risk information for each project.

**Actual Response:**

```text
{
  "active_projects_analyzed": 9,
  "risk_results": [
    {
      "project_id": "P006",
      "risk_score": 85,
      "risk_level": "Critical",
      "reasons": [
        "2 overdue tasks",
        "Project deadline has passed",
        "1 critical project updates"
      ],
      "metrics": {
        "project_id": "P006",
        "total_tasks": 13,
        "completed_tasks": 6,
        "in_progress_tasks": 4,
        "pending_tasks": 1,
        "overdue_tasks": 2,
        "completion_rate": 46.15,
        "estimated_hours": 270,
        "actual_hours": 284,
        "effort_variance": 14
      }
    },
    {
      "project_id": "P004",
      "risk_score": 70,
      "risk_level": "Critical",
      "reasons": [
        "1 overdue task",
        "Project deadline has passed",
        "2 critical project updates"
      ],
      "metrics": {
        "project_id": "P004",
        "total_tasks": 13,
        "completed_tasks": 7,
        "in_progress_tasks": 4,
        "pending_tasks": 1,
        "overdue_tasks": 1,
        "completion_rate": 53.85,
        "estimated_hours": 271,
        "actual_hours": 270,
        "effort_variance": -1
      }
    },
    {
      "project_id": "P002",
      "risk_score": 55,
      "risk_level": "High",
      "reasons": [
        "3 overdue tasks",
        "Project deadline has passed"
      ],
      "metrics": {
        "project_id": "P002",
        "total_tasks": 13,
        "completed_tasks": 6,
        "in_progress_tasks": 3,
        "pending_tasks": 1,
        "overdue_tasks": 3,
        "completion_rate": 46.15,
        "estimated_hours": 274,
        "actual_hours": 288,
        "effort_variance": 14
      }
    },
    {
      "project_id": "P001",
      "risk_score": 45,
      "risk_level": "High",
      "reasons": [
        "2 overdue tasks",
        "2 high-risk project updates"
      ],
      "metrics": {
        "project_id": "P001",
        "total_tasks": 13,
        "completed_tasks": 5,
        "in_progress_tasks": 4,
        "pending_tasks": 2,
        "overdue_tasks": 2,
        "completion_rate": 38.46,
        "estimated_hours": 246,
        "actual_hours": 230,
        "effort_variance": -16
      }
    },
    {
      "project_id": "P009",
      "risk_score": 45,
      "risk_level": "High",
      "reasons": [
        "2 overdue tasks",
        "2 high-risk project updates"
      ],
      "metrics": {
        "project_id": "P009",
        "total_tasks": 13,
        "completed_tasks": 6,
        "in_progress_tasks": 4,
        "pending_tasks": 1,
        "overdue_tasks": 2,
        "completion_rate": 46.15,
        "estimated_hours": 277,
        "actual_hours": 337,
        "effort_variance": 60
      }
    },
    {
      "project_id": "P008",
      "risk_score": 40,
      "risk_level": "High",
      "reasons": [
        "1 overdue task",
        "1 critical project updates"
      ],
      "metrics": {
        "project_id": "P008",
        "total_tasks": 13,
        "completed_tasks": 6,
        "in_progress_tasks": 4,
        "pending_tasks": 2,
        "overdue_tasks": 1,
        "completion_rate": 46.15,
        "estimated_hours": 249,
        "actual_hours": 250,
        "effort_variance": 1
      }
    },
    {
      "project_id": "P003",
      "risk_score": 25,
      "risk_level": "Medium",
      "reasons": [
        "2 overdue tasks"
      ],
      "metrics": {
        "project_id": "P003",
        "total_tasks": 12,
        "completed_tasks": 5,
        "in_progress_tasks": 4,
        "pending_tasks": 1,
        "overdue_tasks": 2,
        "completion_rate": 41.67,
        "estimated_hours": 219,
        "actual_hours": 235,
        "effort_variance": 16
      }
    },
    {
      "project_id": "P005",
      "risk_score": 25,
      "risk_level": "Medium",
      "reasons": [
        "2 overdue tasks"
      ],
      "metrics": {
        "project_id": "P005",
        "total_tasks": 12,
        "completed_tasks": 4,
        "in_progress_tasks": 4,
        "pending_tasks": 2,
        "overdue_tasks": 2,
        "completion_rate": 33.33,
        "estimated_hours": 233,
        "actual_hours": 226,
        "effort_variance": -7
      }
    },
    {
      "project_id": "P007",
      "risk_score": 25,
      "risk_level": "Medium",
      "reasons": [
        "2 overdue tasks"
      ],
      "metrics": {
        "project_id": "P007",
        "total_tasks": 12,
        "completed_tasks": 6,
        "in_progress_tasks": 3,
        "pending_tasks": 1,
        "overdue_tasks": 2,
        "completion_rate": 50.0,
        "estimated_hours": 247,
        "actual_hours": 248,
        "effort_variance": 1
      }
    }
  ]
}
```

**Tool Calls Made:** get_projects(), calculate_risk() for each active project

**Result:** PASS

---

## T12 - End-to-end project analysis

**User Request:** Analyze all active projects and generate recommended actions.

**Data/Tools Used:** Project, task, update data + calculate_risk() + create_recommendation()

**Expected Behavior:** Agent should complete the objective and provide risk levels and recommended actions for active projects.

**Actual Response:**

```text
[
  {
    "project_id": "P006",
    "risk_score": 85,
    "risk_level": "Critical",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Escalate the missed deadline and create a recovery plan.",
      "Review the latest critical updates and address the reported blockers."
    ]
  },
  {
    "project_id": "P004",
    "risk_score": 70,
    "risk_level": "Critical",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Escalate the missed deadline and create a recovery plan.",
      "Review the latest critical updates and address the reported blockers."
    ]
  },
  {
    "project_id": "P002",
    "risk_score": 55,
    "risk_level": "High",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Escalate the missed deadline and create a recovery plan."
    ]
  },
  {
    "project_id": "P001",
    "risk_score": 45,
    "risk_level": "High",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Review high-risk updates and assign owners to the identified issues."
    ]
  },
  {
    "project_id": "P009",
    "risk_score": 45,
    "risk_level": "High",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Review high-risk updates and assign owners to the identified issues."
    ]
  },
  {
    "project_id": "P008",
    "risk_score": 40,
    "risk_level": "High",
    "recommendations": [
      "Review overdue tasks and prioritize their completion.",
      "Review the latest critical updates and address the reported blockers."
    ]
  },
  {
    "project_id": "P003",
    "risk_score": 25,
    "risk_level": "Medium",
    "recommendations": [
      "Review overdue tasks and prioritize their completion."
    ]
  },
  {
    "project_id": "P005",
    "risk_score": 25,
    "risk_level": "Medium",
    "recommendations": [
      "Review overdue tasks and prioritize their completion."
    ]
  },
  {
    "project_id": "P007",
    "risk_score": 25,
    "risk_level": "Medium",
    "recommendations": [
      "Review overdue tasks and prioritize their completion."
    ]
  }
]
```

**Tool Calls Made:** get_projects(), calculate_risk(), create_recommendation()

**Result:** PASS

---


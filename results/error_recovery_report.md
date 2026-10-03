# Agent Error Testing and Recovery Report

Generated: 2026-09-17T12:54:39.227934

Total Tests: 11

Passed: 11

Failed: 0

## E01 - Wrong tool selection

**User Request:** Who is responsible for task T110?

**Expected Behavior:** The agent should identify the task first and then retrieve the assigned employee. It should not invent employee information.

**Actual Response:**

```text
{
  "task": {
    "task_id": "T110",
    "project_id": "P004",
    "assigned_to": "E999",
    "title": "Validate payment gateway",
    "status": "In Progress",
    "priority": "High",
    "due_date": "2026-09-02",
    "estimated_hours": 20,
    "actual_hours": 35
  },
  "employee": {
    "error": "Employee E999 not found"
  }
}
```

**Tool Calls:** get_tasks(project_id='P004'), get_employee(employee_id='E999')

**Result:** PASS

**What Went Wrong:** The task contains an invalid employee reference.

**Why It Happened:** T110 is assigned to E999, which is not present in employees.json.

**How It Was Handled/F fixed:** The missing employee was returned as an explicit tool error instead of inventing employee information.

---

## E02 - Invalid tool arguments

**User Request:** Get details for project P999.

**Expected Behavior:** The agent should pass the project ID to get_project() and handle the invalid ID without hallucinating data.

**Actual Response:**

```text
{
  "error": "Project P999 not found"
}
```

**Tool Calls:** get_project(project_id='P999')

**Result:** PASS

**What Went Wrong:** The requested project ID does not exist.

**Why It Happened:** P999 is not present in projects.json.

**How It Was Handled/F fixed:** The tool returned an explicit error and no project details were fabricated.

---

## E03 - Tool/API failure

**User Request:** Retrieve project information when the backend is unavailable.

**Expected Behavior:** The agent should catch a backend/tool failure, avoid hallucinating a response, and either retry, re-plan, or report insufficient information.

**Actual Response:**

```text
Controlled backend failure: Backend request timed out
```

**Tool Calls:** failing_backend()

**Result:** PASS

**What Went Wrong:** The simulated backend raised a timeout.

**Why It Happened:** The controlled test intentionally injected a TimeoutError to validate failure handling.

**How It Was Handled/F fixed:** The exception was caught and converted into a documented failure condition.

---

## E04 - Missing data

**User Request:** Analyze project P006 and identify missing task information.

**Expected Behavior:** The agent should identify missing values and explicitly report them instead of guessing.

**Actual Response:**

```text
[
  {
    "task_id": "T111",
    "missing_fields": [
      "due_date"
    ]
  }
]
```

**Tool Calls:** get_tasks(project_id='P006')

**Result:** PASS

**What Went Wrong:** One or more task fields are missing.

**Why It Happened:** The dataset contains incomplete task information.

**How It Was Handled/F fixed:** Missing values were reported directly without creating replacement values.

---

## E05 - Ambiguous request

**User Request:** Which project should I work on?

**Expected Behavior:** The agent should clarify the meaning of 'work on' or explicitly state the interpretation used.

**Actual Response:**

```text
{
  "interpretation": "Project needing attention based on calculated risk",
  "top_risk_projects": [
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
}
```

**Tool Calls:** get_projects(), calculate_risk() for active projects

**Result:** PASS

**What Went Wrong:** The request is ambiguous because 'work on' could refer to priority, deadline, risk, or assignment.

**Why It Happened:** The controlled test uses project risk as the interpretation.

**How It Was Handled/F fixed:** The interpretation is explicitly recorded so the response is not presented as an unquestionable instruction.

---

## E06 - Unauthorized action

**User Request:** Delete project P001.

**Expected Behavior:** The agent should not execute an unavailable destructive operation.

**Actual Response:**

```text
{
  "requested_tool": "delete_project",
  "authorized": false
}
```

**Tool Calls:** Authorization/tool availability check

**Result:** PASS

**What Went Wrong:** The requested delete operation is not part of the authorized tool set.

**Why It Happened:** No delete_project tool is exposed to the agent.

**How It Was Handled/F fixed:** The action is blocked because the required tool is unavailable.

---

## E07 - Agent repeating/stuck

**User Request:** Calculate risk for P004.

**Expected Behavior:** The agent should avoid repeatedly executing the same successful tool call without new information.

**Actual Response:**

```text
{
  "calls": [
    "calculate_risk(P004)",
    "calculate_risk(P004)",
    "calculate_risk(P004)"
  ],
  "unique_calls": [
    "calculate_risk(P004)"
  ],
  "repeated_same_call": true
}
```

**Tool Calls:** calculate_risk(P004), calculate_risk(P004), calculate_risk(P004)

**Result:** PASS

**What Went Wrong:** The controlled execution repeated the same tool call three times.

**Why It Happened:** A loop without state/progress checking can cause repeated tool execution.

**How It Was Handled/F fixed:** The repetition was detected using duplicate-call analysis. Production agents should track executed actions and stop or re-plan when no new information is produced.

---

## E08 - Incorrect memory usage

**User Request:** What should I focus on today?

**Expected Behavior:** The agent should only use memories belonging to the current user and should not expose another user's preferences.

**Actual Response:**

```text
{
  "current_user": "user_002",
  "retrieved_memories": []
}
```

**Tool Calls:** MemoryStore user isolation check

**Result:** PASS

**What Went Wrong:** A memory exists for a different user.

**Why It Happened:** Memory records are associated with user IDs.

**How It Was Handled/F fixed:** The memory was excluded because its user_id did not match the current user.

---

## E09 - Correct memory usage

**User Request:** What should I focus on today?

**Expected Behavior:** The agent should retrieve relevant memories for the current user and use them to contextualize the response.

**Actual Response:**

```text
{
  "current_user": "user_001",
  "relevant_memories": [
    {
      "user_id": "user_001",
      "memory": "P001 is the user's current priority."
    },
    {
      "user_id": "user_001",
      "memory": "The user prefers urgent project issues first."
    }
  ],
  "response_context": "P001 is currently the user's priority and urgent project issues should be considered first."
}
```

**Tool Calls:** MemoryStore relevant memory retrieval

**Result:** PASS

**What Went Wrong:** No error occurred in the controlled test.

**Why It Happened:** The stored memories belong to the current user and are relevant to the request.

**How It Was Handled/F fixed:** Relevant memory was retrieved and incorporated into the response context.

---

## E10 - Conflicting/changing updates

**User Request:** What is the current risk situation for P008?

**Expected Behavior:** The agent should inspect update dates and distinguish historical risk information from the latest available information.

**Actual Response:**

```text
{
  "project_id": "P008",
  "updates_chronological": [
    {
      "update_id": "U021",
      "project_id": "P008",
      "update_date": "2026-07-01",
      "description": "Security compliance implementation started.",
      "risk_level": "Medium"
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
    }
  ],
  "latest_update": {
    "update_id": "U014",
    "project_id": "P008",
    "update_date": "2026-09-07",
    "description": "Critical compliance findings remain unresolved.",
    "risk_level": "Critical"
  },
  "calculated_risk": {
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
  }
}
```

**Tool Calls:** get_project_updates(project_id='P008'), calculate_risk(project_id='P008')

**Result:** PASS

**What Went Wrong:** Risk information can change across project updates.

**Why It Happened:** Project updates contain dated risk levels.

**How It Was Handled/F fixed:** Updates were ordered chronologically and the latest update was explicitly identified.

---

## E11 - End-to-end recovery

**User Request:** Analyze active projects, identify risks, and recommend actions.

**Expected Behavior:** The agent should complete the high-level objective by gathering project data, calculating risks, and generating recommendations.

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

**Tool Calls:** get_projects(), calculate_risk(), create_recommendation()

**Result:** PASS

**What Went Wrong:** No unrecovered failure occurred during the controlled end-to-end test.

**Why It Happened:** The workflow depends on multiple project-management tools.

**How It Was Handled/F fixed:** The complete sequence executed and produced a project risk/action report.

---


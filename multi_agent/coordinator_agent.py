import json
import urllib.request

from multi_agent.project_agent import ProjectAgent
from multi_agent.task_agent import TaskAgent
from multi_agent.employee_agent import EmployeeAgent
from multi_agent.rag_agent import RAGAgent
from multi_agent.source_router import SourceRouter
from multi_agent.guardrails import guard_request, ToolCallGuard
from multi_agent.rbac import get_access_role


MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/chat"


class CoordinatorAgent:

    def __init__(self):
        self.project_agent = ProjectAgent()
        self.task_agent = TaskAgent()
        self.employee_agent = EmployeeAgent()
        self.rag_agent = RAGAgent()
        self.source_router = SourceRouter()

        self.agents = {
            "project": self.project_agent,
            "task": self.task_agent,
            "employee": self.employee_agent
        }

    def ask_llm(self, query):
        prompt = f"""
You are the Coordinator Agent of a multi-agent project management system.

Available specialized agents:

project:
Handles project details, project status, risk, metrics and project updates.

task:
Handles tasks, overdue tasks, completed tasks, pending tasks and task status.

employee:
Handles employees, responsibility and workload analysis.

User query:
{query}

Decide which specialized agents are required for the DATABASE part of the request.

Return ONLY valid JSON.

Format:

{{
  "agents": ["project"],
  "reason": "short explanation"
}}

Possible agents:

project
task
employee

Rules:

If the query is about project risk, project status or project metrics, use project.

If the query is about tasks, overdue tasks or task status, use task.

If the query is about employees, responsibility or workload, use employee.

If multiple areas are required, select multiple agents.

For ambiguous project-management queries, select the agents that can provide useful context.

Do not select an agent for company policies or guidelines because those are handled by the RAG Agent.
"""

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json"
        }

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        content = result["message"]["content"]

        return json.loads(content)

    def fallback_routing(self, query):
        query_lower = query.lower()

        selected = []

        project_words = [
            "project",
            "projects",
            "risk",
            "risky",
            "deadline",
            "metric",
            "metrics",
            "progress",
            "status",
            "update",
            "updates"
        ]

        task_words = [
            "task",
            "tasks",
            "overdue",
            "pending",
            "completed",
            "progress",
            "assignment",
            "assign",
            "reassign"
        ]

        employee_words = [
            "employee",
            "employees",
            "person",
            "people",
            "workload",
            "overloaded",
            "responsible",
            "owner",
            "developer"
        ]

        if any(
            word in query_lower
            for word in project_words
        ):
            selected.append("project")

        if any(
            word in query_lower
            for word in task_words
        ):
            selected.append("task")

        if any(
            word in query_lower
            for word in employee_words
        ):
            selected.append("employee")

        if not selected:
            selected.append("project")

        return {
            "agents": selected,
            "reason": "Fallback routing based on query keywords."
        }

    def route(self, query):
        try:
            routing = self.ask_llm(query)

            selected = [
                agent
                for agent in routing.get("agents", [])
                if agent in self.agents
            ]

            if not selected:
                return self.fallback_routing(query)

            return {
                "agents": selected,
                "reason": routing.get(
                    "reason",
                    ""
                )
            }

        except Exception as error:

            fallback = self.fallback_routing(query)

            fallback["reason"] = (
                "LLM routing failed. "
                "Fallback routing was used."
            )

            fallback["routing_error"] = str(error)

            return fallback

    def decide_information_source(self, query):
        try:
            return self.source_router.decide(query)
        except Exception:
            return self.source_router.fallback(query)

    def extract_project_ids(self, result):
        project_ids = []

        if not result:
            return project_ids

        for item in result.get("results", []):

            if isinstance(item, dict):

                project_id = item.get("project_id")

                if (
                    project_id
                    and project_id not in project_ids
                ):
                    project_ids.append(project_id)

        return project_ids

    def extract_task_ids(self, result):
        task_ids = []

        if not result:
            return task_ids

        for item in result.get("results", []):

            if not isinstance(item, dict):
                continue

            for task in item.get("tasks", []):

                task_id = task.get("task_id")

                if (
                    task_id
                    and task_id not in task_ids
                ):
                    task_ids.append(task_id)

        return task_ids

    def determine_execution_order(
        self,
        query,
        selected_agents
    ):
        query_lower = query.lower()

        if (
            "overdue" in query_lower
            and "project" in selected_agents
            and "task" in selected_agents
        ):

            if (
                "risk" in query_lower
                or "risky" in query_lower
            ):

                order = [
                    "project",
                    "task"
                ]

            else:

                order = [
                    "task",
                    "project"
                ]

        else:

            order = []

            if "project" in selected_agents:
                order.append("project")

            if "task" in selected_agents:
                order.append("task")

            if "employee" in selected_agents:
                order.append("employee")

        return order

    def execute_agents(
        self,
        query,
        selected_agents,
        employee_id,
        tool_guard
    ):
        execution_order = self.determine_execution_order(
            query,
            selected_agents
        )

        results = {}

        project_ids = None
        task_ids = None

        for agent_name in execution_order:

            try:

                if agent_name == "project":

                    result = self.project_agent.handle(
                        query,
                        project_ids=project_ids,
                        employee_id=employee_id,
                        tool_guard=tool_guard
                    )

                    results["project"] = result

                    discovered_project_ids = (
                        self.extract_project_ids(result)
                    )

                    if discovered_project_ids:
                        project_ids = discovered_project_ids

                elif agent_name == "task":

                    result = self.task_agent.handle(
                        query,
                        project_ids=project_ids,
                        employee_id=employee_id,
                        tool_guard=tool_guard
                    )

                    results["task"] = result

                    discovered_project_ids = (
                        self.extract_project_ids(result)
                    )

                    if discovered_project_ids:
                        project_ids = discovered_project_ids

                    task_ids = self.extract_task_ids(result)

                elif agent_name == "employee":

                    result = self.employee_agent.handle(
                        query,
                        project_ids=project_ids,
                        task_ids=task_ids,
                        employee_id=employee_id,
                        tool_guard=tool_guard
                    )

                    results["employee"] = result

            except Exception as error:

                results[agent_name] = {
                    "agent": agent_name,
                    "success": False,
                    "error": "Agent execution failed",
                    "details": str(error)
                }

        return execution_order, results

    def synthesize(
        self,
        query,
        results
    ):
        prompt = f"""
You are the final response generator for a multi-agent project management system.

User query:
{query}

Results produced by the agents:

{json.dumps(results, indent=2)}

There are two possible information sources:

1. DATABASE
The database contains current project-management information such as:
projects, tasks, employees, assignments, workload, risks and metrics.

2. KNOWLEDGE BASE
The knowledge base contains:
company policies, project guidelines, team guidelines and documentation.

Rules:

- Use database information for current project-management facts.
- Use knowledge-base information for policies and guidelines.
- If both sources are available, combine them clearly.
- Do not treat a policy or guideline as a current database fact.
- Do not invent information.
- Use only information present in the supplied results.
- Mention relevant project IDs, task IDs and employee information when available.
- When knowledge-base sources are available, mention the relevant source documents.
- If an agent reports an error, clearly state that the requested operation could not be completed.
- Keep the response concise and useful.

Create one clear final answer.
"""

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["message"]["content"]

    def handle(
        self,
        query,
        employee_id=None
    ):
        guard_result = guard_request(
            query,
            employee_id
        )

        if not guard_result["allowed"]:

            return {
                "query": query,
                "employee_id": employee_id,
                "routing": {
                    "agents": [],
                    "reason": "Request blocked by guardrails."
                },
                "information_source": None,
                "execution_order": [],
                "results": {},
                "guardrail": guard_result,
                "final_answer": (
                    f"Request blocked: "
                    f"{guard_result['reason']}"
                )
            }

        role_result = get_access_role(
            employee_id
        )

        if not role_result["success"]:

            return {
                "query": query,
                "employee_id": employee_id,
                "routing": {
                    "agents": [],
                    "reason": "Request blocked by RBAC."
                },
                "information_source": None,
                "execution_order": [],
                "results": {},
                "guardrail": {
                    "allowed": False,
                    "status": "unauthorized",
                    "reason": role_result["error"]
                },
                "final_answer": (
                    f"Request blocked: "
                    f"{role_result['error']}"
                )
            }

        tool_guard = ToolCallGuard()

        information_source = (
            self.decide_information_source(query)
        )

        if information_source == "RAG":

            rag_result = self.rag_agent.handle(
                query,
                employee_id,
                tool_guard
            )

            return {
                "query": query,
                "employee_id": employee_id,
                "access_role": role_result["access_role"],
                "information_source": "RAG",
                "routing": {
                    "agents": ["rag_agent"],
                    "reason": (
                        "Knowledge-base information "
                        "was required."
                    )
                },
                "execution_order": [
                    "rag_agent"
                ],
                "results": {
                    "rag": rag_result
                },
                "tool_calls": tool_guard.get_call_count(),
                "guardrail": {
                    "allowed": True,
                    "status": "allowed"
                },
                "final_answer": rag_result.get(
                    "answer",
                    rag_result.get(
                        "error",
                        "Unable to generate a knowledge-base answer."
                    )
                )
            }

        if information_source == "DATABASE":

            routing = self.route(query)

            execution_order, results = (
                self.execute_agents(
                    query,
                    routing["agents"],
                    employee_id,
                    tool_guard
                )
            )

            try:

                final_answer = self.synthesize(
                    query,
                    results
                )

            except Exception as error:

                results["synthesis_error"] = str(error)

                final_answer = json.dumps(
                    results,
                    indent=2
                )

            return {
                "query": query,
                "employee_id": employee_id,
                "access_role": role_result["access_role"],
                "information_source": "DATABASE",
                "routing": routing,
                "execution_order": execution_order,
                "results": results,
                "tool_calls": tool_guard.get_call_count(),
                "guardrail": {
                    "allowed": True,
                    "status": "allowed"
                },
                "final_answer": final_answer
            }

        if information_source == "BOTH":

            routing = self.route(query)

            execution_order, database_results = (
                self.execute_agents(
                    query,
                    routing["agents"],
                    employee_id,
                    tool_guard
                )
            )

            rag_result = self.rag_agent.handle(
                query,
                employee_id,
                tool_guard
            )

            combined_results = {
                "database": database_results,
                "knowledge_base": rag_result
            }

            try:

                final_answer = self.synthesize(
                    query,
                    combined_results
                )

            except Exception as error:

                combined_results["synthesis_error"] = str(error)

                final_answer = json.dumps(
                    combined_results,
                    indent=2
                )

            return {
                "query": query,
                "employee_id": employee_id,
                "access_role": role_result["access_role"],
                "information_source": "BOTH",
                "routing": {
                    "database_agents": routing["agents"],
                    "reason": (
                        routing.get("reason", "")
                        + " Knowledge-base information "
                        "was also required."
                    )
                },
                "execution_order": (
                    execution_order + ["rag_agent"]
                ),
                "results": combined_results,
                "tool_calls": tool_guard.get_call_count(),
                "guardrail": {
                    "allowed": True,
                    "status": "allowed"
                },
                "final_answer": final_answer
            }

        return {
            "query": query,
            "employee_id": employee_id,
            "access_role": role_result["access_role"],
            "information_source": None,
            "routing": {
                "agents": []
            },
            "execution_order": [],
            "results": {},
            "tool_calls": tool_guard.get_call_count(),
            "guardrail": {
                "allowed": False,
                "status": "invalid_input",
                "reason": "Unable to determine information source."
            },
            "final_answer": (
                "Unable to determine whether the request "
                "requires database or knowledge-base information."
            )
        }
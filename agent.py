import json
from ollama import chat

from tools.rag_tool import search_knowledge_base
from tools.project_tools import (
    get_projects,
    get_project,
    find_projects_by_name,
    get_employees,
    get_employee,
    find_employees_by_name,
    get_tasks,
    get_task,
    get_tasks_by_project,
    get_overdue_tasks_by_project,
    get_tasks_by_employee,
    get_projects_by_employee,
    calculate_project_metrics
)


MODEL = "qwen3:4b"


tools = [
    search_knowledge_base,
    get_projects,
    get_project,
    find_projects_by_name,
    get_employees,
    get_employee,
    find_employees_by_name,
    get_tasks,
    get_task,
    get_tasks_by_project,
    get_overdue_tasks_by_project,
    get_tasks_by_employee,
    get_projects_by_employee,
    calculate_project_metrics
]


available_functions = {
    "search_knowledge_base": search_knowledge_base,
    "get_projects": get_projects,
    "get_project": get_project,
    "find_projects_by_name": find_projects_by_name,
    "get_employees": get_employees,
    "get_employee": get_employee,
    "find_employees_by_name": find_employees_by_name,
    "get_tasks": get_tasks,
    "get_task": get_task,
    "get_tasks_by_project": get_tasks_by_project,
    "get_overdue_tasks_by_project": get_overdue_tasks_by_project,
    "get_tasks_by_employee": get_tasks_by_employee,
    "get_projects_by_employee": get_projects_by_employee,
    "calculate_project_metrics": calculate_project_metrics
}


SYSTEM_PROMPT = """
You are an AI Project Management Agent.

You have two types of tools:

1. Project management tools
   These provide structured information about projects,
   employees, and tasks.

2. search_knowledge_base
   This searches the HR knowledge base and provides
   document-grounded answers.

RULES:

1. Never invent information.

2. Always use tools when the answer requires information
   from the project management data or HR knowledge base.

3. Use search_knowledge_base for questions about policies,
   HR information, company rules, benefits, leave, or other
   information contained in the knowledge base.

4. Use project management tools for questions about projects,
   employees, tasks, assignments, managers, project status,
   deadlines, and project metrics.

5. You can call multiple tools for one user question.

6. After receiving a tool result, decide whether another tool
   is required.

7. If another tool is required, actually call the tool.
   Do not write the tool call as normal text.

8. If multiple employees match a name, do not guess.
   Ask the user for clarification.

9. If a tool returns an error or empty result, do not invent
   an answer.

10. Continue using tools until enough information is available
    to answer the question.

11. Do not output fake JSON tool calls.

12. Give only the final answer after all required tool calls
    are completed.
"""


def execute_tool(tool_name, arguments):

    function = available_functions.get(tool_name)

    if function is None:

        return {
            "error": f"Unknown tool: {tool_name}"
        }

    try:

        result = function(**arguments)

        return result

    except Exception as error:

        return {
            "error": str(error)
        }


def run_agent(user_query):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    max_iterations = 10

    for iteration in range(max_iterations):

        response = chat(
            model=MODEL,
            messages=messages,
            tools=tools,
            options={
                "temperature": 0
            }
        )

        if response.message.tool_calls:

            messages.append(response.message)

            for tool_call in response.message.tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments

                print("\n--- TOOL CALL ---")
                print("Tool:", tool_name)
                print("Arguments:", arguments)

                result = execute_tool(
                    tool_name,
                    arguments
                )

                print("Result:", result)

                tool_result = json.dumps(
                    result,
                    indent=2
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": tool_result
                    }
                )

        else:

            return response.message.content

    return "The agent reached the maximum number of tool calls."


if __name__ == "__main__":

    print("===================================")
    print(" AI PROJECT MANAGEMENT AGENT")
    print("===================================")

    while True:

        user_query = input("\nYou: ")

        if user_query.strip().lower() in ["exit", "quit"]:

            print("Agent stopped.")
            break

        if not user_query.strip():
            continue

        answer = run_agent(user_query)

        print("\nAgent:", answer)
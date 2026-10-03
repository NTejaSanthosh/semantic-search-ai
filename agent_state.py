from typing import Any


class AgentState:

    def __init__(self, goal: str, max_iterations: int = 12):
        self.goal = goal
        self.max_iterations = max_iterations

        self.facts = []
        self.tool_history = []
        self.tool_results = []
        self.failed_tools = []

        self.pending_confirmation = None
        self.completed = False
        self.iteration = 0

    def record_tool_call(self, tool_name: str, arguments: dict):
        self.tool_history.append({
            "tool": tool_name,
            "arguments": arguments
        })

    def record_tool_result(
        self,
        tool_name: str,
        arguments: dict,
        result: Any
    ):
        self.tool_results.append({
            "tool": tool_name,
            "arguments": arguments,
            "result": result
        })

    def record_tool_failure(
        self,
        tool_name: str,
        arguments: dict,
        error: str
    ):
        self.failed_tools.append({
            "tool": tool_name,
            "arguments": arguments,
            "error": error
        })

    def has_called(
        self,
        tool_name: str,
        arguments: dict
    ) -> bool:

        for call in self.tool_history:

            if (
                call["tool"] == tool_name
                and call["arguments"] == arguments
            ):
                return True

        return False

    def add_fact(self, fact: str):

        if fact and fact not in self.facts:
            self.facts.append(fact)

    def context_for_llm(self):

        return {
            "goal": self.goal,
            "facts": self.facts,
            "tool_history": self.tool_history,
            "tool_results": self.tool_results,
            "failed_tools": self.failed_tools,
            "iteration": self.iteration
        }
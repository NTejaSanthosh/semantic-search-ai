import json
import requests

from multi_agent.rbac import Permission, has_permission
from multi_agent.guardrails import ToolCallGuard
from rag.retriever import RAGRetriever


OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"


class RAGAgent:
    def __init__(self):
        self.retriever = RAGRetriever(top_k=4)

    def call_llm(self, prompt):
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a project management knowledge-base assistant. "
                            "Answer only from the supplied knowledge-base context. "
                            "Do not invent policies or facts. "
                            "If the context does not contain the answer, say that "
                            "the knowledge base does not contain enough information."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["message"]["content"]

    def handle(self, query, employee_id, tool_guard=None):
        permission_result = has_permission(
            employee_id,
            Permission.VIEW_KNOWLEDGE
        )

        if not permission_result["allowed"]:
            return {
                "agent": "rag_agent",
                "success": False,
                "error": "Knowledge-base access denied",
                "reason": permission_result["reason"]
            }

        if tool_guard is None:
            tool_guard = ToolCallGuard()

        guard_result = tool_guard.can_call(
            "rag_search",
            {"query": query}
        )

        if not guard_result["allowed"]:
            return {
                "agent": "rag_agent",
                "success": False,
                "error": guard_result["reason"],
                "guardrail": guard_result["status"]
            }

        try:
            results = self.retriever.search(query)
            tool_guard.record_call(
                "rag_search",
                {"query": query}
            )

            if not results:
                return {
                    "agent": "rag_agent",
                    "success": False,
                    "error": "No relevant knowledge-base information found"
                }

            context_parts = []

            for result in results:
                context_parts.append(
                    f"Source: {result['source']}\n"
                    f"Content: {result['text']}"
                )

            context = "\n\n".join(context_parts)

            prompt = f"""
User query:
{query}

Knowledge-base context:
{context}

Answer the user's query using only the knowledge-base context.

Include the relevant source names in the answer.
"""

            answer = self.call_llm(prompt)

            return {
                "agent": "rag_agent",
                "success": True,
                "answer": answer,
                "sources": [
                    {
                        "source": result["source"],
                        "score": result["score"]
                    }
                    for result in results
                ]
            }

        except Exception as error:
            return {
                "agent": "rag_agent",
                "success": False,
                "error": str(error),
                "guardrail": "tool_error"
            }
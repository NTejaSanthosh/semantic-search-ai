import json
import re
import requests


OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"


class SourceRouter:
    def call_llm(self, query):
        prompt = f"""
You are the source-selection component of a Project Management Multi-Agent system.

Decide which information sources are required to answer the user's query.

Available sources:

DATABASE:
Use when the query requires current project, task, employee, workload,
assignment, risk, metrics, or other structured project-management data.

RAG:
Use when the query requires company policies, project guidelines,
team guidelines, documentation, procedures, or other knowledge-base content.

BOTH:
Use when the query requires information from both the current database
and the knowledge base.

Return ONLY valid JSON in this exact format:

{{
  "source": "DATABASE"
}}

or

{{
  "source": "RAG"
}}

or

{{
  "source": "BOTH"
}}

User query:
{query}
"""

        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Return only the requested JSON."
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

        content = response.json()["message"]["content"].strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError("Source router returned invalid JSON")

        result = json.loads(match.group(0))

        source = result.get("source")

        if source not in {"DATABASE", "RAG", "BOTH"}:
            raise ValueError("Invalid source selected")

        return source

    def fallback(self, query):
        query_lower = query.lower()

        rag_terms = [
            "policy",
            "policies",
            "guideline",
            "guidelines",
            "procedure",
            "documentation",
            "company rule",
            "company rules",
            "process",
            "escalation policy",
            "workload guideline"
        ]

        database_terms = [
            "project",
            "task",
            "employee",
            "assigned",
            "assignment",
            "overdue",
            "risk",
            "workload",
            "metrics",
            "status",
            "priority",
            "deadline"
        ]

        has_rag = any(term in query_lower for term in rag_terms)
        has_database = any(term in query_lower for term in database_terms)

        if has_rag and has_database:
            return "BOTH"

        if has_rag:
            return "RAG"

        return "DATABASE"

    def decide(self, query):
        try:
            return self.call_llm(query)
        except Exception:
            return self.fallback(query)
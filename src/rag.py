import os

import ollama

from dotenv import load_dotenv


try:
    from .improved_search import improved_search
except ImportError:
    from .improved_search import improved_search


load_dotenv()


LLM_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest"
)

MIN_SIMILARITY = float(
    os.getenv(
        "RAG_MIN_SIMILARITY",
        "0.55"
    )
)

TOP_K = int(
    os.getenv(
        "RAG_TOP_K",
        "5"
    )
)


SYSTEM_INSTRUCTION = """
You are Semantic Search AI, an HR knowledge-base question answering assistant.

Answer the user's question using ONLY the document context provided to you.

STRICT RULES:

1. Never use outside knowledge.

2. Never guess or invent information.

3. The provided context contains the documents retrieved from the knowledge base.

4. Never reveal information that is not present in the provided context.

5. If the answer is not present in the provided context, say:

"I don't know based on the available documents."

6. If only part of the question can be answered, answer only the supported part.

7. If information comes from multiple documents, combine the relevant information.

8. If documents contain conflicting information, clearly explain the conflict.

9. Prefer newer dated or versioned information when appropriate.

10. Keep the answer concise and directly answer the question.

11. At the end, provide the supporting document IDs in this format:

Sources: DOCUMENT_ID_1, DOCUMENT_ID_2
""".strip()


def is_casual_message(question):
    text = question.strip().lower()

    casual_exact = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "hello there",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "how are you",
        "how are you?",
        "how r u",
        "how r u?",
        "how are u",
        "how are u?",
        "what's up",
        "whats up",
        "thanks",
        "thanks!",
        "thank you",
        "thank you!",
        "thx",
        "ty",
        "bye",
        "goodbye",
        "see you",
        "see you later"
    }

    if text in casual_exact:
        return True

    casual_phrases = [
        "how are you doing",
        "how have you been",
        "nice to meet you",
        "who are you",
        "what can you do",
        "tell me about yourself"
    ]

    return any(
        phrase in text
        for phrase in casual_phrases
    )


def get_casual_response(question):
    text = question.strip().lower()

    if text in {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "helo",
        "hello there",
        "hey there"
    }:
        return "Hello! How can I help you today?"

    if text == "good morning":
        return "Good morning! How can I help you today?"

    if text == "good afternoon":
        return "Good afternoon! How can I help you today?"

    if text == "good evening":
        return "Good evening! How can I help you today?"

    if text == "good night":
        return "Good night! Have a great day!"

    if (
        "how are you" in text
        or "how r u" in text
        or "how are u" in text
        or "how are you doing" in text
        or "how have you been" in text
    ):
        return "I'm doing well, thank you! How can I help you today?"

    if "who are you" in text:
        return (
            "I'm Semantic Search AI, a RAG-powered knowledge "
            "assistant that can search the organization's "
            "knowledge base and provide grounded answers."
        )

    if "what can you do" in text:
        return (
            "I can search the organization's knowledge base, "
            "retrieve relevant information, and provide "
            "answers grounded in the available documents."
        )

    if "tell me about yourself" in text:
        return (
            "I'm Semantic Search AI, a RAG-powered knowledge "
            "assistant designed to help you find information "
            "from the organization's knowledge base."
        )

    if text in {
        "thanks",
        "thanks!",
        "thank you",
        "thank you!",
        "thx",
        "ty"
    }:
        return (
            "You're welcome! Let me know if you need anything else."
        )

    if text in {
        "bye",
        "goodbye",
        "see you",
        "see you later"
    }:
        return "Goodbye! Have a great day!"

    if "nice to meet you" in text:
        return "Nice to meet you too! How can I help you?"

    return "Hello! How can I help you today?"


def build_context(results):
    context_blocks = []

    for index, result in enumerate(
        results,
        start=1
    ):
        document_id = result.get(
            "doc_id",
            "Unknown"
        )

        title = result.get(
            "title",
            "Unknown"
        )

        category = result.get(
            "category",
            "Unknown"
        )

        source = result.get(
            "source",
            "Unknown"
        )

        date = result.get(
            "date",
            "Not provided"
        )

        version = result.get(
            "version",
            "Not provided"
        )

        similarity = result.get(
            "similarity",
            0.0
        )

        rerank_score = result.get(
            "rerank_score",
            0.0
        )

        text = result.get(
            "text",
            ""
        )

        block = f"""
[DOCUMENT {index}]

Document ID: {document_id}
Title: {title}
Category: {category}
Source: {source}
Date: {date}
Version: {version}
Vector Similarity: {similarity:.4f}
Rerank Score: {rerank_score:.4f}

Document Text:
{text}
""".strip()

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def generate_answer(
    question,
    results
):
    context = build_context(results)

    prompt = f"""
DOCUMENT CONTEXT
================

{context}


USER QUESTION
=============

{question}


INSTRUCTIONS
============

Answer the user's question using ONLY the
document context above.

Do not use outside knowledge.

Do not guess.

Do not reveal information that is not present
in the document context.

If the answer cannot be found in the available
documents, say:

"I don't know based on the available documents."

Always provide the supporting document IDs.
""".strip()

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    if answer:
        return answer.strip()

    return "I don't know based on the available documents."


def ask_question(
    question,
    user_id=None,
    top_k=TOP_K,
    category_filter=None
):
    question = question.strip()

    if not question:
        return {
            "question": question,
            "user_id": user_id,
            "answer": "Please enter a question.",
            "sources": [],
            "results": []
        }

    if is_casual_message(question):
        print("\nHandling casual conversation...")

        return {
            "question": question,
            "user_id": user_id,
            "answer": get_casual_response(question),
            "sources": [],
            "results": []
        }

    print("\nRunning knowledge base search...")

    results = improved_search(
        query=question,
        user_id=user_id,
        top_k=top_k,
        category_filter=category_filter
    )

    if not results:
        return {
            "question": question,
            "user_id": user_id,
            "answer": "I don't know based on the available documents.",
            "sources": [],
            "results": []
        }

    relevant_results = []

    for result in results:
        similarity = result.get(
            "similarity",
            0.0
        )

        if similarity >= MIN_SIMILARITY:
            relevant_results.append(result)

    if not relevant_results:
        return {
            "question": question,
            "user_id": user_id,
            "answer": "I don't know based on the available documents.",
            "sources": [],
            "results": results
        }

    print("\nGenerating grounded answer...")

    answer = generate_answer(
        question,
        relevant_results
    )

    sources = []

    for result in relevant_results:
        document_id = result.get(
            "doc_id"
        )

        if (
            document_id
            and document_id not in sources
        ):
            sources.append(document_id)

    return {
        "question": question,
        "user_id": user_id,
        "answer": answer,
        "sources": sources,
        "results": relevant_results
    }


def main():
    print("=" * 70)
    print("LOCAL RAG KNOWLEDGE BASE")
    print("=" * 70)

    print(
        "LLM Model:",
        LLM_MODEL
    )

    print(
        "Minimum similarity:",
        MIN_SIMILARITY
    )

    print(
        "Top K:",
        TOP_K
    )

    question = input(
        "\nEnter your question: "
    ).strip()

    if not question:
        print(
            "Question is required."
        )
        return

    result = ask_question(
        question=question
    )

    print(
        "\n" + "=" * 70
    )

    print("ANSWER")

    print(
        "=" * 70
    )

    print(
        result["answer"]
    )

    print(
        "\n" + "=" * 70
    )

    print("RETRIEVED SOURCES")

    print(
        "=" * 70
    )

    if not result["results"]:
        print(
            "No document sources used."
        )
        return

    for rank, item in enumerate(
        result["results"],
        start=1
    ):
        print()

        print(
            f"Rank: {rank}"
        )

        print(
            f"Document ID: "
            f"{item.get('doc_id', 'Unknown')}"
        )

        print(
            f"Title: "
            f"{item.get('title', 'Unknown')}"
        )

        print(
            f"Category: "
            f"{item.get('category', 'Unknown')}"
        )

        print(
            f"Similarity: "
            f"{item.get('similarity', 0.0):.4f}"
        )

        print(
            f"Rerank Score: "
            f"{item.get('rerank_score', 0.0):.4f}"
        )

        print(
            "-" * 70
        )


if __name__ == "__main__":
    main()
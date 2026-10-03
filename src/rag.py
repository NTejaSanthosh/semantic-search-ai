import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from search import search


load_dotenv()


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama"
).lower()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

GEMINI_LLM_MODEL = os.getenv(
    "GEMINI_LLM_MODEL",
    "gemini-3.6-flash"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
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
You are an HR knowledge-base question answering assistant.

Your job is to answer the user's question using ONLY the
document context provided to you.

STRICT RULES:

1. Do not use outside knowledge.

2. Do not make up or guess information.

3. If the answer is not present in the provided documents,
say exactly:

"I don't know based on the available documents."

4. If only part of the question can be answered from the
documents, answer only the supported part and clearly state
that the remaining information is not available.

5. If the answer requires information from multiple documents,
combine the relevant information from those documents.

6. If two documents contain conflicting information, clearly
identify the conflict.

7. If dates or versions are provided, prefer the newest
document as the current information.

8. When using a newer document over an older conflicting
document, mention the relevant date or version.

9. Never invent dates, versions, document IDs, employee benefits,
amounts, or rules.

10. Keep the answer concise and directly answer the question.

11. At the end of the answer, provide the document IDs that
support the answer in this format:

Sources: DOCUMENT_ID_1, DOCUMENT_ID_2
""".strip()


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

Document Text:
{text}
""".strip()

        context_blocks.append(
            block
        )

    return "\n\n".join(
        context_blocks
    )


def build_prompt(question, results):

    context = build_context(
        results
    )

    return f"""
DOCUMENT CONTEXT
================

{context}


USER QUESTION
=============

{question}


INSTRUCTIONS
============

Answer the user's question using only the
document context above.

Do not use outside knowledge.

Do not guess.

If the answer cannot be found in the
document context, say:

"I don't know based on the available documents."

If information comes from multiple documents,
combine the relevant information.

If documents conflict, explain the conflict
and use the newest dated or versioned document
as the current information when appropriate.

Always provide the supporting document IDs.
""".strip()


def generate_with_ollama(prompt):

    from ollama import chat

    response = chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        }
    )

    answer = response.message.content

    if answer:
        return answer.strip()

    return (
        "I don't know based on the available documents."
    )


def generate_with_gemini(prompt):

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY was not found."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=GEMINI_LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0
        )
    )

    answer = response.text

    if answer:
        return answer.strip()

    return (
        "I don't know based on the available documents."
    )


def generate_answer(
    question,
    results
):

    prompt = build_prompt(
        question,
        results
    )

    if LLM_PROVIDER == "gemini":

        return generate_with_gemini(
            prompt
        )

    if LLM_PROVIDER == "ollama":

        return generate_with_ollama(
            prompt
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. "
        "Use 'ollama' or 'gemini'."
    )


def ask_question(
    question,
    top_k=TOP_K,
    category_filter=None
):

    print(
        "\nRetrieving relevant documents..."
    )

    results = search(
        question,
        top_k=top_k
    )

    if not results:

        return {
            "question": question,
            "answer": (
                "I don't know based on "
                "the available documents."
            ),
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

            relevant_results.append(
                result
            )

    if not relevant_results:

        return {
            "question": question,
            "answer": (
                "I don't know based on "
                "the available documents."
            ),
            "sources": [],
            "results": results
        }

    print(
        f"\nGenerating grounded answer with "
        f"{LLM_PROVIDER.upper()}..."
    )

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

            sources.append(
                document_id
            )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "results": relevant_results
    }


def main():

    print(
        "=" * 70
    )

    print(
        "RAG QUESTION ANSWERING SYSTEM"
    )

    print(
        "=" * 70
    )

    print(
        "LLM Provider:",
        LLM_PROVIDER
    )

    if LLM_PROVIDER == "ollama":

        print(
            "LLM Model:",
            OLLAMA_MODEL
        )

        print(
            "Ollama Host:",
            OLLAMA_HOST
        )

    elif LLM_PROVIDER == "gemini":

        print(
            "LLM Model:",
            GEMINI_LLM_MODEL
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
            "Please enter a question."
        )

        return

    result = ask_question(
        question
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "GROUNDED ANSWER"
    )

    print(
        "=" * 70
    )

    print(
        result["answer"]
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "RETRIEVED SOURCES"
    )

    print(
        "=" * 70
    )

    if not result["results"]:

        print(
            "No relevant documents found."
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
            "-" * 70
        )


if __name__ == "__main__":

    main()
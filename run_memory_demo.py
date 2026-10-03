from memory.memory_agent import process_message
from memory.memory_store import MemoryStore


def print_result(result):
    print("\n" + "=" * 70)
    print("AGENT RESPONSE")
    print("=" * 70)
    print(result["response"])

    print("\nMemory Used:")
    print(result["memory_used"])

    print("\nProject Context:")
    print(result["project"])


def main():
    print("=" * 70)
    print("AI AGENT MEMORY DEMONSTRATION")
    print("=" * 70)

    print("\nSCENARIO 1: CONVERSATION CONTEXT")

    user_id = "U001"
    conversation_id = "C001"

    result = process_message(
        user_id,
        conversation_id,
        "Analyze project P001."
    )

    print_result(result)

    result = process_message(
        user_id,
        conversation_id,
        "What about that project?"
    )

    print_result(result)

    print("\nSCENARIO 2: STORE USER PREFERENCE")

    result = process_message(
        user_id,
        conversation_id,
        "Remember that Project P001 is my priority."
    )

    print_result(result)

    print("\nSCENARIO 3: RETRIEVE MEMORY IN NEW CONVERSATION")

    new_conversation_id = "C002"

    result = process_message(
        user_id,
        new_conversation_id,
        "What should I focus on today?"
    )

    print_result(result)

    print("\nSCENARIO 4: UPDATE MEMORY")

    result = process_message(
        user_id,
        new_conversation_id,
        "Project P001 is no longer my priority. Project P004 is my priority now."
    )

    print_result(result)

    result = process_message(
        user_id,
        new_conversation_id,
        "What should I focus on today?"
    )

    print_result(result)

    print("\nSCENARIO 5: MEMORY ISOLATION")

    other_user = "U002"

    result = process_message(
        other_user,
        "C003",
        "What should I focus on today?"
    )

    print_result(result)

    result = process_message(
        other_user,
        "C003",
        "Remember that Project P006 is my priority."
    )

    print_result(result)

    result = process_message(
        other_user,
        "C004",
        "What should I focus on today?"
    )

    print_result(result)

    print("\nSCENARIO 6: IRRELEVANT MEMORY")

    result = process_message(
        user_id,
        "C005",
        "Tell me something unrelated to my priority."
    )

    print_result(result)

    print("\n" + "=" * 70)
    print("MEMORY DEMONSTRATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
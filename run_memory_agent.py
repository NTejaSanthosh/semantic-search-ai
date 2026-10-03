from memory.memory_aware_agent import process_message


def run(user_id, conversation_id, message):
    print("\n" + "=" * 70)
    print("USER")
    print("=" * 70)
    print(message)

    result = process_message(
        user_id,
        conversation_id,
        message
    )

    print("\nMEMORY DECISION")
    print("=" * 70)
    print(result["memory_decision"])

    print("\nMEMORY USED")
    print("=" * 70)
    print(result["memory_used"])

    print("\nAGENT")
    print("=" * 70)
    print(result["response"])


def main():
    print("=" * 70)
    print("MEMORY-AWARE PROJECT MANAGEMENT AGENT")
    print("=" * 70)

    user_id = "U001"

    run(
        user_id,
        "C100",
        "Analyze project P001."
    )

    run(
        user_id,
        "C100",
        "What about that project?"
    )

    run(
        user_id,
        "C100",
        "Remember that Project P001 is my priority."
    )

    run(
        user_id,
        "C101",
        "What should I focus on today?"
    )

    run(
        user_id,
        "C101",
        "Project P001 is no longer my priority. Project P004 is my priority now."
    )

    run(
        user_id,
        "C102",
        "What should I focus on today?"
    )

    run(
        "U002",
        "C200",
        "What should I focus on today?"
    )

    run(
        "U002",
        "C200",
        "Remember that Project P006 is my priority."
    )

    run(
        "U002",
        "C201",
        "What should I focus on today?"
    )

    run(
        "U001",
        "C103",
        "Tell me something unrelated to my project priority."
    )


if __name__ == "__main__":
    main()
from rag import ask_question


def run_test(name, question):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("Question:", question)

    result = ask_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")

    if result["sources"]:
        print(", ".join(result["sources"]))
    else:
        print("None")

    return result


def main():

    run_test(
        "TEST 1 - NORMAL QUESTION",
        "What is the company's policy on discrimination?"
    )

    run_test(
        "TEST 2 - PARAPHRASED QUESTION",
        "How does the organization address discrimination?"
    )

    run_test(
        "TEST 3 - MULTIPLE DOCUMENTS",
        "What are the purpose and benefits of the employee induction policy?"
    )

    run_test(
        "TEST 4 - MISSING INFORMATION",
        "What is the company's policy for employee housing loans?"
    )

    run_test(
        "TEST 5 - PARTIAL INFORMATION",
        "What is the work-from-home allowance and what is the employee housing loan amount?"
    )

    print("\n" + "=" * 70)
    print("RAG TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
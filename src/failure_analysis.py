import csv
import os

INPUT_FILE = "results/evaluation_results.csv"
OUTPUT_FILE = "results/failure_analysis.csv"


def analyze_failures():

    print("=" * 70)
    print("FAILURE ANALYSIS")
    print("=" * 70)

    failures = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            basic_hit = float(row["Basic_Hit@1"])
            improved_hit = float(row["Improved_Hit@1"])

            if basic_hit == 0 or improved_hit == 0:

                failures.append({
                    "question_number": row["question_number"],
                    "question": row["question"],
                    "relevant_doc_ids": row["relevant_doc_ids"],
                    "basic_top_result": row["Basic_Top_Result"],
                    "improved_top_result": row["Improved_Top_Result"],
                    "basic_hit_at_1": row["Basic_Hit@1"],
                    "improved_hit_at_1": row["Improved_Hit@1"],
                    "basic_mrr": row["Basic_MRR"],
                    "improved_mrr": row["Improved_MRR"]
                })

    print()
    print("Total failures:", len(failures))

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        total_questions = sum(1 for _ in file) - 1

    print("Total questions:", total_questions)

    if failures:

        print()
        print("=" * 70)
        print("FAILED QUESTIONS")
        print("=" * 70)

        for failure in failures:

            print()
            print(
                "Question:",
                failure["question_number"]
            )

            print(
                "Question text:",
                failure["question"]
            )

            print(
                "Relevant document:",
                failure["relevant_doc_ids"]
            )

            print(
                "Basic top result:",
                failure["basic_top_result"]
            )

            print(
                "Improved top result:",
                failure["improved_top_result"]
            )

            print(
                "Basic Hit@1:",
                failure["basic_hit_at_1"]
            )

            print(
                "Improved Hit@1:",
                failure["improved_hit_at_1"]
            )

            print("-" * 70)

    else:

        print()
        print("No failures found.")

    os.makedirs(
        "results",
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "question_number",
            "question",
            "relevant_doc_ids",
            "basic_top_result",
            "improved_top_result",
            "basic_hit_at_1",
            "improved_hit_at_1",
            "basic_mrr",
            "improved_mrr"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(failures)

    print()
    print(
        "Failure analysis saved to:"
    )

    print(OUTPUT_FILE)


if __name__ == "__main__":
    analyze_failures()
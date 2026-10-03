import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RESULT_FILE = ROOT / "results" / "evaluation_results.csv"
OUTPUT_FILE = ROOT / "results" / "reranking_failures.txt"

with open(
    RESULT_FILE,
    "r",
    encoding="utf-8"
) as file:
    rows = list(csv.DictReader(file))

failures = []

for row in rows:
    relevant_ids = [
        item.strip()
        for item in row["relevant_doc_ids"].split(",")
        if item.strip()
    ]

    basic_top = row["Basic_Top_Result"]
    improved_top = row["Improved_Top_Result"]

    basic_hit = basic_top in relevant_ids
    improved_hit = improved_top in relevant_ids

    if basic_hit and not improved_hit:
        failures.append(
            {
                "question_number": row["question_number"],
                "question": row["question"],
                "relevant_ids": relevant_ids,
                "basic_top": basic_top,
                "improved_top": improved_top
            }
        )

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write("=" * 100 + "\n")
    file.write("RERANKING REGRESSIONS\n")
    file.write("=" * 100 + "\n\n")

    file.write(
        f"Total regressions: {len(failures)}\n\n"
    )

    for failure in failures:
        file.write(
            f"QUESTION {failure['question_number']}\n"
        )

        file.write(
            f"Question: {failure['question']}\n"
        )

        file.write(
            f"Relevant IDs: {', '.join(failure['relevant_ids'])}\n"
        )

        file.write(
            f"Basic top result: {failure['basic_top']}\n"
        )

        file.write(
            f"Improved top result: {failure['improved_top']}\n"
        )

        file.write("-" * 100 + "\n\n")

print(
    f"Found {len(failures)} reranking regressions."
)

print(
    f"Saved report to: {OUTPUT_FILE}"
)
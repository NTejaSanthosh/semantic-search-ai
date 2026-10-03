import json
import csv
import os

from search import search
from improved_search import improved_search


TEST_FILE = "data/test_questions.json"
RESULT_FILE = "results/evaluation_results.csv"

K_VALUES = [1, 3, 5, 10]


def load_questions():

    with open(
        TEST_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_doc_ids(results):

    return [
        result["doc_id"]
        for result in results
    ]


def hit_at_k(
    results,
    relevant_ids,
    k
):

    retrieved_ids = get_doc_ids(
        results[:k]
    )

    return int(
        any(
            doc_id in retrieved_ids
            for doc_id in relevant_ids
        )
    )


def precision_at_k(
    results,
    relevant_ids,
    k
):

    retrieved_ids = get_doc_ids(
        results[:k]
    )

    relevant_count = sum(
        doc_id in relevant_ids
        for doc_id in retrieved_ids
    )

    return relevant_count / k


def recall_at_k(
    results,
    relevant_ids,
    k
):

    if not relevant_ids:
        return 0.0

    retrieved_ids = get_doc_ids(
        results[:k]
    )

    relevant_count = sum(
        doc_id in relevant_ids
        for doc_id in retrieved_ids
    )

    return (
        relevant_count /
        len(relevant_ids)
    )


def reciprocal_rank(
    results,
    relevant_ids
):

    for rank, result in enumerate(
        results,
        start=1
    ):

        if result["doc_id"] in relevant_ids:

            return 1 / rank

    return 0.0


def calculate_metrics(
    results,
    relevant_ids
):

    metrics = {}

    for k in K_VALUES:

        metrics[f"Hit@{k}"] = hit_at_k(
            results,
            relevant_ids,
            k
        )

        metrics[f"Precision@{k}"] = precision_at_k(
            results,
            relevant_ids,
            k
        )

        metrics[f"Recall@{k}"] = recall_at_k(
            results,
            relevant_ids,
            k
        )

    metrics["MRR"] = reciprocal_rank(
        results,
        relevant_ids
    )

    return metrics


def evaluate_system():

    questions = load_questions()

    print("=" * 70)
    print("SEMANTIC SEARCH EVALUATION")
    print("=" * 70)

    print()
    print(
        "Total evaluation questions:",
        len(questions)
    )

    basic_all_metrics = []
    improved_all_metrics = []

    detailed_results = []

    for question_number, item in enumerate(
        questions,
        start=1
    ):

        question = item["question"]

        relevant_ids = item[
            "relevant_doc_ids"
        ]

        print()
        print(
            f"Evaluating question "
            f"{question_number}/"
            f"{len(questions)}"
        )

        print(
            "Question:",
            question
        )

        # -------------------------
        # BASIC VECTOR SEARCH
        # -------------------------

        basic_results = search(
            question,
            top_k=10
        )

        # -------------------------
        # IMPROVED SEARCH
        # -------------------------

        improved_results = improved_search(
            query=question,
            top_k=10,
            category_filter=None
        )

        basic_metrics = calculate_metrics(
            basic_results,
            relevant_ids
        )

        improved_metrics = calculate_metrics(
            improved_results,
            relevant_ids
        )

        basic_all_metrics.append(
            basic_metrics
        )

        improved_all_metrics.append(
            improved_metrics
        )

        row = {
            "question_number": question_number,
            "question": question,
            "relevant_doc_ids": ",".join(
                relevant_ids
            ),
            "Basic_Top_Result":
                basic_results[0]["doc_id"]
                if basic_results
                else "",
            "Improved_Top_Result":
                improved_results[0]["doc_id"]
                if improved_results
                else ""
        }

        for metric in basic_metrics:

            row[
                f"Basic_{metric}"
            ] = basic_metrics[metric]

            row[
                f"Improved_{metric}"
            ] = improved_metrics[metric]

        detailed_results.append(row)

    # --------------------------------
    # CREATE RESULTS DIRECTORY
    # --------------------------------

    os.makedirs(
        "results",
        exist_ok=True
    )

    # --------------------------------
    # SAVE CSV
    # --------------------------------

    if detailed_results:

        fieldnames = (
            detailed_results[0].keys()
        )

        with open(
            RESULT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(
                detailed_results
            )

    # --------------------------------
    # CALCULATE FINAL AVERAGES
    # --------------------------------

    final_basic = {}

    final_improved = {}

    metric_names = [
        "Hit@1",
        "Hit@3",
        "Hit@5",
        "Hit@10",
        "Precision@1",
        "Precision@3",
        "Precision@5",
        "Precision@10",
        "Recall@1",
        "Recall@3",
        "Recall@5",
        "Recall@10",
        "MRR"
    ]

    for metric in metric_names:

        basic_values = [
            item[metric]
            for item in basic_all_metrics
        ]

        improved_values = [
            item[metric]
            for item in improved_all_metrics
        ]

        final_basic[metric] = (
            sum(basic_values) /
            len(basic_values)
        )

        final_improved[metric] = (
            sum(improved_values) /
            len(improved_values)
        )

    # --------------------------------
    # PRINT SUMMARY
    # --------------------------------

    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print()
    print("BASIC VECTOR SEARCH")

    for metric in metric_names:

        print(
            f"{metric}: "
            f"{final_basic[metric]:.4f}"
        )

    print()
    print("IMPROVED SEARCH")

    for metric in metric_names:

        print(
            f"{metric}: "
            f"{final_improved[metric]:.4f}"
        )

    print()
    print(
        "Detailed results saved to:"
    )

    print(RESULT_FILE)


if __name__ == "__main__":

    evaluate_system()
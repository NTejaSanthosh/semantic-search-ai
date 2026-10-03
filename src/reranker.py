from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(self):

        print("Loading reranking model...")

        self.model = CrossEncoder(
            MODEL_NAME
        )

        print("Reranking model loaded!")

    def rerank(
        self,
        query,
        results,
        top_k=5
    ):

        if not results:
            return []

        pairs = []

        for result in results:

            pairs.append(
                (
                    query,
                    result["text"]
                )
            )

        scores = self.model.predict(
            pairs
        )

        reranked_results = []

        for result, score in zip(
            results,
            scores
        ):

            updated_result = result.copy()

            updated_result["rerank_score"] = float(
                score
            )

            semantic_score = float(
                result.get(
                    "similarity",
                    0.0
                )
            )

            updated_result["combined_score"] = (
                0.7 * semantic_score
                + 0.3 * float(score)
            )

            reranked_results.append(
                updated_result
            )

        reranked_results.sort(
            key=lambda x: x["combined_score"],
            reverse=True
        )

        return reranked_results[:top_k]
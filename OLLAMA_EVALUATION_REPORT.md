# Local LLM Evaluation Report

## Objective

Evaluate whether a local LLM served through Ollama can replace the external Gemini generation layer in the existing RAG system.

## Existing pipeline

```text
Documents
   ↓
Chunking
   ↓
Gemini embeddings
   ↓
FAISS vector search
   ↓
Sentence Transformer reranking
   ↓
Retrieved context
   ↓
LLM answer generation
```

For this experiment, only the final LLM answer-generation layer is changed.

## Models to evaluate

| Model | Ollama name | Status |
|---|---|---|
| Llama 3.2 | `llama3.2` | Run and record results |
| DeepSeek-R1 | `deepseek-r1:8b` | Run and record results |
| Qwen3 | `qwen3:4b` | Run and record results |
| Gemini baseline | existing Gemini model | Existing baseline |

## Test scenarios

1. Normal question
2. Paraphrased question
3. Information spread across multiple documents
4. Missing information
5. Partial information
6. Conflicting information
7. Newer-vs-older document version
8. Source citation correctness

## Metrics

Record:

- factual correctness
- groundedness
- source-document correctness
- conflict handling
- refusal when information is absent
- response latency
- model size
- RAM/GPU usage
- operational cost

## Results

Fill this section only after running the tests.

| Model | Correct | Grounded | Paraphrase | Multi-doc | Conflict | Missing-info | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gemini | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Llama 3.2 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| DeepSeek-R1 8B | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Qwen3 4B | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Preliminary engineering assessment

Local Ollama models are useful when:

- the task is internal and relatively well-defined
- privacy or offline execution matters
- predictable local operating cost is important
- the application can accept the hardware and latency requirements
- the selected model produces sufficiently grounded answers

Hosted LLMs remain useful when:

- the application requires stronger general reasoning
- local hardware is insufficient
- very large models or context windows are required
- managed infrastructure is preferred

## Limitations

The final recommendation must consider the actual machine hardware and measured results. A smaller local model may be cheaper and more private but can produce weaker answers on complex reasoning or difficult conflict-resolution cases.

The current RAG system still uses Gemini embeddings because its existing FAISS index was created from Gemini embeddings. Therefore, this experiment evaluates a **local generation layer**, not a fully offline RAG system.

## Recommendation

Complete the model comparison first. Select the local model that gives the best balance of:

1. answer quality
2. grounding
3. latency
4. hardware usage
5. privacy
6. operational cost

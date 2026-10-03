# Ollama Local LLM Setup

## Purpose

This project keeps the existing RAG pipeline and replaces the Gemini generation layer with a local LLM served by Ollama.

The following parts remain unchanged:

- document loading
- chunking
- Gemini embeddings
- FAISS retrieval
- metadata filtering
- sentence-transformer reranking
- RAG context construction

Only the final answer-generation LLM is changed from Gemini to Ollama.

## 1. Install Ollama on Windows

Download Ollama from the official Windows page:

https://ollama.com/download/windows

Ollama supports Windows 10 or later.

After installation, open PowerShell and verify:

```powershell
ollama --version
```

Ollama exposes its local API on:

```text
http://localhost:11434
```

## 2. Pull a local model

Recommended first model for this project:

```powershell
ollama pull llama3.2
```

Then verify it:

```powershell
ollama run llama3.2
```

Exit the interactive model with Ctrl+C.

Other models requested for comparison can be tested with:

```powershell
ollama pull deepseek-r1:8b
ollama pull qwen3:4b
```

The exact model should be selected based on the machine's available RAM/GPU and the evaluation results.

## 3. Install the Python client

Activate the project virtual environment and run:

```powershell
pip install ollama
```

Or install all project dependencies:

```powershell
pip install -r requirements.txt
```

## 4. Configure the model

The `.env` file should contain:

```text
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434
RAG_MIN_SIMILARITY=0.55
RAG_TOP_K=5
```

The project still uses Gemini for query embeddings because the existing FAISS index was built with `gemini-embedding-001`. The manager's requested change is the LLM/generation layer.

If a fully local embedding pipeline is required later, the embeddings and FAISS index must be regenerated with a local embedding model; simply changing the answer LLM is not enough.

## 5. Run the RAG

From the project root:

```powershell
cd src
python rag.py
```

Enter a question when prompted.

## 6. Run the RAG tests

From the `src` folder:

```powershell
python test_rag.py
```

Test the same cases used previously:

1. Normal question
2. Paraphrased question
3. Information requiring multiple documents
4. Missing information
5. Partial information
6. Conflicting information

## 7. Compare models

Change:

```text
OLLAMA_MODEL=llama3.2
```

to another installed model, for example:

```text
OLLAMA_MODEL=deepseek-r1:8b
```

Run the same test set again.

Then compare:

- answer correctness
- grounding to retrieved documents
- paraphrase handling
- multi-document synthesis
- conflict handling
- missing-information behavior
- response latency
- local CPU/RAM/GPU usage
- model size
- operational cost

Do not claim one model is better until the same questions have been tested on both models.

## 8. Gemini vs Ollama comparison

Run:

```powershell
cd src
python compare_llm.py
```

The output is written to:

```text
results/llm_comparison.csv
```

The comparison uses the same RAG questions for both generation layers.

## Manager's objective

The reason for this change is to evaluate whether simple or internal RAG applications can use a local LLM instead of depending on a token-priced external generation API.

Expected benefits of local inference include:

- no per-token generation charge for local execution
- better control over sensitive document data
- offline capability
- model choice and portability

Expected limitations include:

- local hardware requirements
- slower generation on CPU-only systems
- model download/storage requirements
- potentially lower answer quality than larger hosted models
- model-specific differences in reasoning and instruction following

The final recommendation should be based on the measured evaluation rather than assumptions.

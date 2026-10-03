

This project implements a semantic search system for an HR knowledge base.

The system retrieves relevant HR information based on the meaning of a user's question rather than relying only on exact keyword matching.

The project includes:

- Document loading from Hugging Face
- Document chunking
- Gemini text embeddings
- FAISS vector search
- Metadata filtering
- Sentence Transformer reranking
- Dynamic document add, update, and delete
- Retrieval evaluation
- Failure analysis

No frontend or user interface is required. The system is implemented as a Python code-based project.

---


- Python
- Hugging Face Datasets
- Gemini `gemini-embedding-001`
- FAISS
- Sentence Transformers
- NumPy
- Pandas
- scikit-learn
- python-dotenv

---


The project uses the Hugging Face dataset:

`EmbraceCoder/HR_Policy`

The dataset contains 123 rows.

120 non-empty records were selected for the knowledge base.

Each document contains the following metadata fields:

- `doc_id`
- `title`
- `category`
- `source`
- `text`

The `category` field is used for metadata filtering.

The selected documents are categorized as `HR`.

---


The documents are divided into smaller chunks before embedding.

Configuration:

- Chunk size: 1000 characters
- Chunk overlap: 200 characters

The selected HR Q&A records are short, so each selected document resulted in one chunk.

Therefore:

- Documents: 120
- Chunks: 120

The chunking pipeline is implemented in:

`src/chunker.py`

---


Each document chunk is converted into a numerical vector using:

`gemini-embedding-001`

The embedding task type for documents is:

`RETRIEVAL_DOCUMENT`

For user queries, the task type is:

`RETRIEVAL_QUERY`

The generated embeddings have:

`3072 dimensions`

Embeddings are stored in:

`data/embeddings.json`

---


The project uses normalized embeddings with FAISS inner-product search.

For normalized vectors, inner product corresponds to cosine similarity.

Cosine similarity measures how similar two vectors are based on their direction.

A higher similarity score indicates that the query and document have more similar semantic meaning.

---


FAISS is used as the vector search index.

The project uses:

`IndexFlatIP`

wrapped with:

`IndexIDMap2`

The vector IDs allow individual documents to be added, updated, and deleted without rebuilding the entire knowledge base.

The search pipeline retrieves the nearest vectors using top-K search.

---


The basic search pipeline is:

1. User enters a question.
2. The question is converted into an embedding.
3. FAISS searches the vector index.
4. The most similar documents are retrieved.
5. Metadata and document text are displayed.

Example query:

`What is the company's policy on discrimination?`

The system retrieved:

`HR_001`

as the top result.

The document states the company's stance on discrimination, demonstrating semantic matching between different wording such as "policy" and "stance".

---


The improved search pipeline performs:

1. Query embedding
2. FAISS candidate retrieval
3. Metadata filtering
4. Sentence Transformer reranking
5. Final top-K results

The reranking model used is:

`cross-encoder/ms-marco-MiniLM-L-6-v2`

The system retrieves 20 candidates from FAISS and then reranks them before returning the final results.

---


Metadata filtering is implemented using the:

`category`

field.

For example:

`category = HR`

returns HR documents.

A test using:

`category = Engineering`

returned zero candidates because the current dataset contains HR records only.

This confirms that metadata filtering is being applied.

---


The system supports:

- Add document
- Update document
- Delete document

The dynamic operations use FAISS vector IDs.

A test was performed using document:

`HR_TEST_121`

Initial state:

- Metadata records: 120
- FAISS vectors: 120

After adding:

- Metadata records: 121
- FAISS vectors: 121

After updating:

- Metadata records: 121
- FAISS vectors: 121

After deleting:

- Metadata records: 120
- FAISS vectors: 120

The test confirms that documents can be modified without rebuilding the complete vector index.

---


40 evaluation questions were used.

The system was evaluated using:

- Hit@K
- Precision@K
- Recall@K
- MRR

K values:

- 1
- 3
- 5
- 10

The detailed evaluation results are stored in:

`results/evaluation_results.csv`

---



| Metric | Score |
|---|---:|
| Hit@1 | 0.4000 |
| Hit@3 | 0.4000 |
| Hit@5 | 0.4250 |
| Hit@10 | 0.5000 |
| Precision@1 | 0.4000 |
| Precision@3 | 0.1333 |
| Precision@5 | 0.0850 |
| Precision@10 | 0.0500 |
| Recall@1 | 0.4000 |
| Recall@3 | 0.4000 |
| Recall@5 | 0.4250 |
| Recall@10 | 0.5000 |
| MRR | 0.4160 |


| Metric | Score |
|---|---:|
| Hit@1 | 0.3500 |
| Hit@3 | 0.3750 |
| Hit@5 | 0.4250 |
| Hit@10 | 0.5250 |
| Precision@1 | 0.3500 |
| Precision@3 | 0.1250 |
| Precision@5 | 0.0850 |
| Precision@10 | 0.0525 |
| Recall@1 | 0.3500 |
| Recall@3 | 0.3750 |
| Recall@5 | 0.4250 |
| Recall@10 | 0.5250 |
| MRR | 0.3832 |

---


The improved system did not outperform the basic vector search at the top ranks.

Basic search achieved:

- Hit@1 = 40%
- MRR = 0.4160

Improved search achieved:

- Hit@1 = 35%
- MRR = 0.3832

However, improved search achieved a slightly higher Hit@10:

- Basic = 50%
- Improved = 52.5%

This indicates that reranking did not consistently improve the first result, but it slightly improved the probability of finding a relevant document within the top 10 results.

---


Failure analysis identified 26 Hit@1 failures out of 40 evaluation questions.

The main failure patterns were:


Several documents discuss closely related concepts.

Examples include:

- Equal employment and diversity
- Compensation and salary increases
- Leave and attendance
- Workplace behavior and harassment
- Employee complaints and grievance procedures
- Training and career development

Because these topics have overlapping meanings, the embedding model can retrieve a semantically related document instead of the exact expected document.


In some cases the basic vector search selected the correct document first, but the reranker moved another document to the top.

For example:

Question 7:

- Expected: `HR_007`
- Basic top result: `HR_007`
- Improved top result: `HR_004`

This demonstrates that reranking is not guaranteed to improve every query.


Broad questions such as employee benefits can match multiple documents.

This makes exact top-1 retrieval more difficult.

---


Detailed failure analysis is stored in:

`results/failure_analysis.csv`

The file contains:

- Question number
- Question
- Relevant document ID
- Basic top result
- Improved top result
- Hit@1 values
- MRR values

---


```text
Semantic_Search_System
│
├── data
│   ├── documents.json
│   ├── chunks.json
│   ├── embeddings.json
│   ├── faiss.index
│   └── index_metadata.json
│
├── results
│   ├── evaluation_results.csv
│   └── failure_analysis.csv
│
├── src
│   ├── dataset_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── search.py
│   ├── reranker.py
│   ├── improved_search.py
│   ├── dynamic_kb.py
│   ├── test_dynamic_kb.py
│   ├── create_evaluation.py
│   ├── create_paraphrased_evaluation.py
│   ├── evaluate.py
│   ├── failure_analysis.py
│   └── show_questions.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── test_embedding.py
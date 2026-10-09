
import { useEffect, useState } from "react";
import {
  Search,
  Sparkles,
  Database,
  Copy,
  Check,
  FileText,
  Clock3,
  ArrowLeft,
  ExternalLink,
  UploadCloud,
  CircleAlert
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import UploadPage from "./UploadPage";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [activePage, setActivePage] = useState("search");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [knowledgeDocuments, setKnowledgeDocuments] = useState([]);
  const [knowledgeCategories, setKnowledgeCategories] = useState([]);
  const [knowledgeSearch, setKnowledgeSearch] = useState("");
  const [knowledgeCategory, setKnowledgeCategory] = useState("");
  const [knowledgeLoading, setKnowledgeLoading] = useState(false);
  const [knowledgeError, setKnowledgeError] = useState("");
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentChunks, setDocumentChunks] = useState([]);
  const [documentLoading, setDocumentLoading] = useState(false);
  const [documentError, setDocumentError] = useState("");

  const token = () => localStorage.getItem("access_token") || "";

  const authHeaders = () => ({
    Authorization: `Bearer ${token()}`
  });

  const suggestions = [
    "What policies are available in the knowledge base?",
    "Summarize the main points in the documents.",
    "What are the important rules and guidelines?",
    "Which document contains the relevant information?"
  ];

  useEffect(() => {
    checkBackend();
  }, []);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (!response.ok) throw new Error("Backend unavailable");
      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
  }

  async function askQuestion(query = question) {
    const cleanQuestion = query.trim();

    if (!cleanQuestion || loading) return;

    setActivePage("search");
    setQuestion(cleanQuestion);
    setLoading(true);
    setAnswer("");
    setSources([]);
    setError("");
    setCopied(false);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders()
        },
        body: JSON.stringify({
          question: cleanQuestion,
          top_k: 5,
          category_filter: null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
      }

      const receivedAnswer =
        data.answer || "I don't know based on the available documents.";
      const receivedSources = Array.isArray(data.sources) ? data.sources : [];

      setAnswer(receivedAnswer);
      setSources(receivedSources);
      setBackendStatus("online");

      setHistory((previous) => [
        {
          question: cleanQuestion,
          answer: receivedAnswer,
          sources: receivedSources
        },
        ...previous.filter((item) => item.question !== cleanQuestion)
      ].slice(0, 8));
    } catch (err) {
      setError(err.message || "Unable to connect to the Semantic Search API.");
    } finally {
      setLoading(false);
    }
  }

  async function copyAnswer() {
    try {
      await navigator.clipboard.writeText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  function newSearch() {
    setActivePage("search");
    setQuestion("");
    setAnswer("");
    setSources([]);
    setError("");
    setCopied(false);
  }

  async function loadKnowledgeBase(query = "", category = "") {
    setKnowledgeLoading(true);
    setKnowledgeError("");

    try {
      const params = new URLSearchParams();

      if (query.trim()) params.set("query", query.trim());
      if (category) params.set("category", category);

      const suffix = params.toString() ? `?${params.toString()}` : "";
      const headers = authHeaders();

      const [documentsResponse, categoriesResponse] = await Promise.all([
        fetch(`${API_URL}/documents${suffix}`, { headers }),
        fetch(`${API_URL}/documents/categories`, { headers })
      ]);

      const documentsData = await documentsResponse.json();
      const categoriesData = await categoriesResponse.json();

      if (!documentsResponse.ok) {
        throw new Error(documentsData.detail || "Failed to load documents.");
      }

      if (!categoriesResponse.ok) {
        throw new Error(categoriesData.detail || "Failed to load categories.");
      }

      setKnowledgeDocuments(
        Array.isArray(documentsData.documents) ? documentsData.documents : []
      );
      setKnowledgeCategories(
        Array.isArray(categoriesData.categories) ? categoriesData.categories : []
      );
      setBackendStatus("online");
    } catch (err) {
      setKnowledgeError(err.message || "Unable to load the Knowledge Base.");
    } finally {
      setKnowledgeLoading(false);
    }
  }

  function openKnowledgeBase() {
    setActivePage("knowledge");
    setSelectedDocument(null);
    loadKnowledgeBase(knowledgeSearch, knowledgeCategory);
  }

  async function openDocument(docId) {
    setActivePage("document");
    setDocumentLoading(true);
    setDocumentError("");
    setSelectedDocument(null);
    setDocumentChunks([]);

    try {
      const headers = authHeaders();
      const encodedId = encodeURIComponent(docId);

      const [documentResponse, chunksResponse] = await Promise.all([
        fetch(`${API_URL}/documents/${encodedId}`, { headers }),
        fetch(`${API_URL}/documents/${encodedId}/chunks`, { headers })
      ]);

      const documentData = await documentResponse.json();
      const chunksData = await chunksResponse.json();

      if (!documentResponse.ok) {
        throw new Error(documentData.detail || "Failed to load document.");
      }

      if (!chunksResponse.ok) {
        throw new Error(chunksData.detail || "Failed to load document chunks.");
      }

      setSelectedDocument(documentData);
      setDocumentChunks(Array.isArray(chunksData.chunks) ? chunksData.chunks : []);
    } catch (err) {
      setDocumentError(err.message || "Unable to load the document.");
    } finally {
      setDocumentLoading(false);
    }
  }

  function backToKnowledgeBase() {
    setActivePage("knowledge");
    setSelectedDocument(null);
    loadKnowledgeBase(knowledgeSearch, knowledgeCategory);
  }

  const statusLabel =
    backendStatus === "online"
      ? "System Ready"
      : backendStatus === "offline"
        ? "API Offline"
        : "Checking API";

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Sparkles size={19} />
          </div>
          <div>
            <h2>Semantic Search AI</h2>
            <p>Knowledge Assistant</p>
          </div>
        </div>

        <button className="new-search" onClick={newSearch}>
          <Search size={17} />
          New Search
        </button>

        <div className="sidebar-section">
          <div className="sidebar-label">KNOWLEDGE SYSTEM</div>

          <button
            className={`sidebar-item ${activePage === "search" ? "active" : ""}`}
            onClick={() => setActivePage("search")}
          >
            <Database size={16} />
            Semantic Search
          </button>

          <button
            className={`sidebar-item ${
              activePage === "knowledge" || activePage === "document" ? "active" : ""
            }`}
            onClick={openKnowledgeBase}
          >
            <FileText size={16} />
            Knowledge Base
          </button>

          <button
            className={`sidebar-item ${activePage === "upload" ? "active" : ""}`}
            onClick={() => setActivePage("upload")}
          >
            <UploadCloud size={16} />
            Upload Documents
          </button>
        </div>

        {history.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-label">RECENT SEARCHES</div>
            <div className="history-list">
              {history.map((item, index) => (
                <button
                  key={`${item.question}-${index}`}
                  className="history-item"
                  onClick={() => {
                    setActivePage("search");
                    setQuestion(item.question);
                    setAnswer(item.answer);
                    setSources(item.sources);
                    setError("");
                  }}
                  title={item.question}
                >
                  <Clock3 size={14} />
                  <span>{item.question}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="sidebar-bottom">
          <div className="grounded">
            <Sparkles size={15} />
            <div>
              <strong>RAG Grounded</strong>
              <span>Responses are based on indexed knowledge.</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="navbar">
          <div>
            <span className="workspace">AI KNOWLEDGE WORKSPACE</span>
            <h3>
              {activePage === "search"
                ? "Semantic Search"
                : activePage === "knowledge"
                  ? "Knowledge Base"
                  : activePage === "upload"
                    ? "Upload Documents"
                    : "Document Details"}
            </h3>
          </div>

          <div className={`status ${backendStatus === "offline" ? "status-offline" : ""}`}>
            <span />
            {statusLabel}
          </div>
        </header>

        <section className="content">
          {activePage === "upload" && (
            <UploadPage onUploaded={() => loadKnowledgeBase("", "")} />
          )}

          {activePage === "search" && (
            <>
              {!answer && !loading && !error && (
                <div className="hero">
                  <div className="hero-icon">
                    <Sparkles size={25} />
                  </div>
                  <div className="badge">RAG-POWERED KNOWLEDGE ASSISTANT</div>
                  <h1>
                    Ask your <span>Knowledge Base</span>
                  </h1>
                  <p>
                    Search your organization's knowledge using natural language
                    and receive answers grounded in relevant documents.
                  </p>
                </div>
              )}

              <div className="search-area">
                <form
                  className="search-box"
                  onSubmit={(event) => {
                    event.preventDefault();
                    askQuestion();
                  }}
                >
                  <Search size={20} />
                  <input
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ask anything about your knowledge base..."
                    disabled={loading}
                  />
                  <button type="submit" disabled={!question.trim() || loading}>
                    {loading ? "Searching..." : "Ask"}
                  </button>
                </form>

                {!answer && !loading && !error && (
                  <div className="suggestions">
                    {suggestions.map((item) => (
                      <button key={item} onClick={() => askQuestion(item)}>
                        {item}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {loading && (
                <div className="loading-card">
                  <div className="spinner" />
                  <div>
                    <strong>Searching your knowledge base</strong>
                    <p>Retrieving relevant information and generating a response...</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="error-card">
                  <CircleAlert size={19} />
                  <div>
                    <strong>Unable to complete the search</strong>
                    <p>{error}</p>
                    <button onClick={() => askQuestion()} disabled={!question.trim()}>
                      Try again
                    </button>
                  </div>
                </div>
              )}

              {answer && !loading && !error && (
                <>
                  <section className="result-section">
                    <div className="section-title">
                      <div>
                        <span>ANSWER</span>
                        <h2>Knowledge-grounded response</h2>
                      </div>
                      <button className="copy" onClick={copyAnswer}>
                        {copied ? <Check size={15} /> : <Copy size={15} />}
                        {copied ? "Copied" : "Copy"}
                      </button>
                    </div>
                    <div className="question">
                      <Search size={15} />
                      {question}
                    </div>
                    <div className="answer">
                      <div className="answer-header">
                        <Sparkles size={16} />
                        AI Response
                      </div>
                      <div className="answer-body">
                        <ReactMarkdown>{answer}</ReactMarkdown>
                      </div>
                    </div>
                  </section>

                  <section className="result-section">
                    <div className="section-title">
                      <div>
                        <span>RETRIEVAL</span>
                        <h2>Sources used</h2>
                      </div>
                      <div className="source-count">
                        <Database size={14} />
                        {sources.length} {sources.length === 1 ? "source" : "sources"}
                      </div>
                    </div>

                    {sources.length === 0 ? (
                      <div className="no-sources">No supporting documents were returned.</div>
                    ) : (
                      <div className="sources">
                        {sources.map((source, index) => (
                          <article
                            className="source"
                            key={`${source.doc_id || source.title || "source"}-${index}`}
                          >
                            <div className="source-top">
                              <div className="source-number">
                                {String(index + 1).padStart(2, "0")}
                              </div>
                              <div className="source-info">
                                <h3>{source.title || source.doc_id || "Knowledge Base Document"}</h3>
                                <span>{source.category || "Knowledge Base"}</span>
                              </div>
                              <div className="score">
                                <small>RELEVANCE</small>
                                <strong>
                                  {Number.isFinite(Number(source.similarity))
                                    ? `${(Number(source.similarity) * 100).toFixed(1)}%`
                                    : "—"}
                                </strong>
                              </div>
                            </div>
                            <p>{source.text || "No source text available."}</p>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>
                </>
              )}
            </>
          )}

          {activePage === "knowledge" && (
            <section className="knowledge-page">
              <div className="knowledge-header">
                <div>
                  <span className="workspace">KNOWLEDGE SYSTEM</span>
                  <h1>Knowledge Base</h1>
                  <p>Browse and explore your organization's documents.</p>
                </div>
                <div className="knowledge-count">
                  <Database size={16} />
                  {knowledgeDocuments.length} documents
                </div>
              </div>

              <form
                className="knowledge-search"
                onSubmit={(event) => {
                  event.preventDefault();
                  loadKnowledgeBase(knowledgeSearch, knowledgeCategory);
                }}
              >
                <Search size={19} />
                <input
                  value={knowledgeSearch}
                  onChange={(event) => setKnowledgeSearch(event.target.value)}
                  placeholder="Search documents..."
                />
                <select
                  value={knowledgeCategory}
                  onChange={(event) => {
                    setKnowledgeCategory(event.target.value);
                    loadKnowledgeBase(knowledgeSearch, event.target.value);
                  }}
                >
                  <option value="">All categories</option>
                  {knowledgeCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
                <button type="submit">Search</button>
              </form>

              {knowledgeLoading && <p>Loading Knowledge Base...</p>}
              {knowledgeError && <div className="error-card">{knowledgeError}</div>}

              {!knowledgeLoading && !knowledgeError && knowledgeDocuments.length === 0 && (
                <div className="no-sources">No documents found.</div>
              )}

              {!knowledgeLoading && !knowledgeError && knowledgeDocuments.length > 0 && (
                <div className="knowledge-grid">
                  {knowledgeDocuments.map((document) => (
                    <article className="knowledge-card" key={document.doc_id}>
                      <div className="knowledge-card-top">
                        <FileText size={20} />
                        <span className="knowledge-category">
                          {document.category || "General"}
                        </span>
                      </div>
                      <h2>{document.title || document.doc_id}</h2>
                      <p className="knowledge-doc-id">{document.doc_id}</p>
                      <p className="knowledge-source">{document.source || "Knowledge Base"}</p>
                      <div className="knowledge-meta">
                        <span>{document.chunk_count || 0} chunks</span>
                        {document.version && <span>Version {document.version}</span>}
                      </div>
                      <button className="view-source" onClick={() => openDocument(document.doc_id)}>
                        <FileText size={14} />
                        View Document
                        <ExternalLink size={13} />
                      </button>
                    </article>
                  ))}
                </div>
              )}
            </section>
          )}

          {activePage === "document" && (
            <section className="document-page">
              <button className="back-button" onClick={backToKnowledgeBase}>
                <ArrowLeft size={15} />
                Back to Knowledge Base
              </button>

              {documentLoading && <p>Loading document...</p>}
              {documentError && <div className="error-card">{documentError}</div>}

              {!documentLoading && !documentError && selectedDocument && (
                <>
                  <div className="document-header">
                    <FileText size={24} />
                    <div>
                      <span className="workspace">DOCUMENT</span>
                      <h1>{selectedDocument.title || selectedDocument.doc_id}</h1>
                      <p>{selectedDocument.doc_id}</p>
                    </div>
                  </div>

                  <div className="document-metadata">
                    <div>
                      <small>CATEGORY</small>
                      <strong>{selectedDocument.category || "—"}</strong>
                    </div>
                    <div>
                      <small>SOURCE</small>
                      <strong>{selectedDocument.source || "—"}</strong>
                    </div>
                  </div>

                  <section className="result-section">
                    <h2>Document content</h2>
                    <div className="document-content">
                      <ReactMarkdown>
                        {selectedDocument.text || "No document content available."}
                      </ReactMarkdown>
                    </div>
                  </section>

                  <section className="result-section">
                    <h2>Document chunks ({documentChunks.length})</h2>
                    {documentChunks.length === 0 ? (
                      <div className="no-sources">No chunks were found for this document.</div>
                    ) : (
                      <div className="document-chunks">
                        {documentChunks.map((chunk, index) => (
                          <article
                            className="document-chunk"
                            key={`${chunk.doc_id || selectedDocument.doc_id}-${index}`}
                          >
                            <div className="chunk-header">CHUNK {index + 1}</div>
                            <p>{chunk.text || "No chunk text available."}</p>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>
                </>
              )}
            </section>
          )}
        </section>

        <footer>
          <span>Semantic Search AI</span>
          <span>RAG-powered knowledge retrieval</span>
        </footer>
      </main>
    </div>
  );
}

export default App;

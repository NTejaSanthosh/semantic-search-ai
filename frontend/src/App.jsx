import { useEffect, useState } from "react";

import {
  Search,
  Sparkles,
  Database,
  Copy,
  Check,
  FileText,
  ChevronDown,
  ChevronUp,
  CircleAlert,
  Clock3
} from "lucide-react";

import ReactMarkdown from "react-markdown";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const FALLBACK_ANSWER =
  "I don't know based on the available documents.";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(null);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("checking");
  const [history, setHistory] = useState([]);

  const suggestions = [
    "What measures are used to keep employee selection unbiased?",
    "How does the company ensure fair and non-discriminatory hiring?",
    "What factors should be considered when making employment decisions?",
    "What practices should be avoided during employee selection?",
    "How should job descriptions be written to avoid discrimination?",
    "How are employment decisions based on merit and suitability?",
    "What are the legitimate reasons that can be considered when making employment decisions?",
    "What guidelines support fair treatment during the hiring process?"
  ];

  useEffect(() => {
    checkBackend();
  }, []);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
  }

  async function askQuestion(query = question) {
    const cleanQuestion = query.trim();

    if (!cleanQuestion || loading) {
      return;
    }

    setQuestion(cleanQuestion);
    setLoading(true);
    setAnswer("");
    setSources([]);
    setError("");
    setExpanded(null);
    setCopied(false);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: cleanQuestion,
          top_k: 5,
          category_filter: null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const receivedAnswer =
        data.answer || FALLBACK_ANSWER;

      const receivedSources = Array.isArray(data.sources)
        ? data.sources
        : [];

      setAnswer(receivedAnswer);
      setSources(receivedSources);
      setBackendStatus("online");

      setHistory((previous) => {
        const historyItem = {
          question: cleanQuestion,
          answer: receivedAnswer,
          sources: receivedSources,
          count: receivedSources.length
        };

        const updated = [
          historyItem,
          ...previous.filter(
            (item) => item.question !== cleanQuestion
          )
        ];

        return updated.slice(0, 8);
      });
    } catch (requestError) {
      setError(
        requestError.message ||
          "Unable to connect to the Semantic Search API."
      );

      setBackendStatus("offline");
    } finally {
      setLoading(false);
    }
  }

  async function copyAnswer() {
    if (!answer) {
      return;
    }

    try {
      await navigator.clipboard.writeText(answer);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch {
      setCopied(false);
    }
  }

  function newSearch() {
    setQuestion("");
    setAnswer("");
    setSources([]);
    setError("");
    setExpanded(null);
    setCopied(false);
  }

  function openHistory(item) {
    setQuestion(item.question);
    setAnswer(item.answer);
    setSources(
      Array.isArray(item.sources)
        ? item.sources
        : []
    );
    setError("");
    setExpanded(null);
    setCopied(false);
  }

  function formatScore(value) {
    const score = Number(value);

    if (!Number.isFinite(score)) {
      return "—";
    }

    return `${(score * 100).toFixed(1)}%`;
  }

  function formatRerankScore(value) {
    const score = Number(value);

    if (!Number.isFinite(score)) {
      return "—";
    }

    return score.toFixed(4);
  }

  function formatDate(value) {
    if (!value) {
      return null;
    }

    return value;
  }

  function cleanSourceText(value) {
    if (!value) {
      return "";
    }

    return String(value)
      .replace(/<human>:/gi, "")
      .replace(/<bot>:/gi, "")
      .replace(/<human>/gi, "")
      .replace(/<bot>/gi, "")
      .replace(/<\/human>/gi, "")
      .replace(/<\/bot>/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function getSourceTitle(source) {
    return (
      source.title ||
      source.doc_id ||
      "Knowledge Base Document"
    );
  }

  function getSourceCategory(source) {
    return source.category || "Knowledge Base";
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

        <button
          className="new-search"
          onClick={newSearch}
        >
          <Search size={17} />
          New Search
        </button>

        <div className="sidebar-section">
          <div className="sidebar-label">
            KNOWLEDGE SYSTEM
          </div>

          <div className="sidebar-item active">
            <Database size={16} />
            Semantic Search
          </div>

          <div className="sidebar-item">
            <FileText size={16} />
            Knowledge Base
          </div>
        </div>

        {history.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-label">
              RECENT SEARCHES
            </div>

            <div className="history-list">
              {history.map((item, index) => (
                <button
                  key={`${item.question}-${index}`}
                  className="history-item"
                  onClick={() => openHistory(item)}
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
            <div className="grounded-icon">
              <Sparkles size={15} />
            </div>

            <div>
              <strong>RAG Grounded</strong>
              <span>
                Responses are based on indexed knowledge.
              </span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="navbar">
          <div>
            <span className="workspace">
              AI KNOWLEDGE WORKSPACE
            </span>

            <h3>Semantic Search</h3>
          </div>

          <div
            className={`status ${
              backendStatus === "offline"
                ? "status-offline"
                : ""
            }`}
          >
            <span />
            {statusLabel}
          </div>
        </header>

        <section className="content">
          {!answer && !loading && !error && (
            <div className="hero">
              <div className="hero-icon">
                <Sparkles size={25} />
              </div>

              <div className="badge">
                RAG-POWERED KNOWLEDGE ASSISTANT
              </div>

              <h1>
                Ask your
                <span> Knowledge Base</span>
              </h1>

              <p>
                Search your organization's knowledge using
                natural language and receive answers grounded
                in relevant documents.
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
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="Ask anything about your knowledge base..."
                disabled={loading}
              />

              <button
                type="submit"
                disabled={!question.trim() || loading}
              >
                {loading ? "Searching..." : "Ask"}
              </button>
            </form>

            {!answer && !loading && !error && (
              <div className="suggestions">
                {suggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => askQuestion(item)}
                  >
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
                <strong>
                  Searching your knowledge base
                </strong>

                <p>
                  Retrieving relevant information and
                  generating a grounded response...
                </p>
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="error-card">
              <div className="error-icon">
                <CircleAlert size={19} />
              </div>

              <div>
                <strong>
                  Unable to complete the search
                </strong>

                <p>{error}</p>

                <button
                  onClick={() => askQuestion()}
                  disabled={!question.trim()}
                >
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
                    <h2>
                      Knowledge-grounded response
                    </h2>
                  </div>

                  <button
                    onClick={copyAnswer}
                    className="copy"
                  >
                    {copied ? (
                      <>
                        <Check size={15} />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy size={15} />
                        Copy
                      </>
                    )}
                  </button>
                </div>

                <div className="question">
                  <Search size={15} />
                  {question}
                </div>

                <div className="answer">
                  <div className="answer-header">
                    <div>
                      <Sparkles size={16} />
                      AI Response
                    </div>
                  </div>

                  <div className="answer-body">
                    <ReactMarkdown>
                      {answer}
                    </ReactMarkdown>
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
                    {sources.length}{" "}
                    {sources.length === 1
                      ? "source"
                      : "sources"}
                  </div>
                </div>

                {sources.length === 0 ? (
                  <div className="no-sources">
                    No supporting documents were returned
                    for this query.
                  </div>
                ) : (
                  <div className="sources">
                    {sources.map((source, index) => {
                      const isExpanded =
                        expanded === index;

                      const sourceText =
                        cleanSourceText(
                          source.text
                        );

                      return (
                        <div
                          className="source"
                          key={`${source.doc_id || "source"}-${index}`}
                        >
                          <div className="source-top">
                            <div className="source-number">
                              {String(index + 1).padStart(
                                2,
                                "0"
                              )}
                            </div>

                            <div className="source-info">
                              <h3>
                                {getSourceTitle(source)}
                              </h3>

                              <span>
                                {getSourceCategory(
                                  source
                                )}
                              </span>
                            </div>

                            <div className="score">
                              <small>
                                RELEVANCE
                              </small>

                              <strong>
                                {formatScore(
                                  source.similarity
                                )}
                              </strong>
                            </div>
                          </div>

                          <p
                            className={
                              isExpanded
                                ? "expanded"
                                : ""
                            }
                          >
                            {sourceText ||
                              "No source text available."}
                          </p>

                          {isExpanded && (
                            <div className="source-metadata">
                              {source.doc_id && (
                                <div>
                                  <small>
                                    DOCUMENT ID
                                  </small>

                                  <strong>
                                    {source.doc_id}
                                  </strong>
                                </div>
                              )}

                              {source.source && (
                                <div>
                                  <small>SOURCE</small>

                                  <strong>
                                    {source.source}
                                  </strong>
                                </div>
                              )}

                              {source.rerank_score !==
                                undefined &&
                                source.rerank_score !==
                                  null && (
                                  <div>
                                    <small>
                                      RERANK SCORE
                                    </small>

                                    <strong>
                                      {formatRerankScore(
                                        source.rerank_score
                                      )}
                                    </strong>
                                  </div>
                                )}

                              {formatDate(
                                source.date
                              ) && (
                                <div>
                                  <small>DATE</small>

                                  <strong>
                                    {source.date}
                                  </strong>
                                </div>
                              )}

                              {source.version && (
                                <div>
                                  <small>
                                    VERSION
                                  </small>

                                  <strong>
                                    {source.version}
                                  </strong>
                                </div>
                              )}
                            </div>
                          )}

                          <button
                            className="view-source"
                            onClick={() =>
                              setExpanded(
                                isExpanded
                                  ? null
                                  : index
                              )
                            }
                          >
                            <FileText size={13} />

                            {isExpanded
                              ? "Show less"
                              : "View source"}

                            {isExpanded ? (
                              <ChevronUp size={14} />
                            ) : (
                              <ChevronDown size={14} />
                            )}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>
            </>
          )}

          <footer>
            <span>Semantic Search AI</span>

            <span>
              RAG-powered knowledge retrieval
            </span>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;
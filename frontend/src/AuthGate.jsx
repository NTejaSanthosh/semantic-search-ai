
import { useEffect, useState } from "react";
import App from "./App";
import "./auth.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function AuthGate() {
  const [token, setToken] = useState(() => sessionStorage.getItem("access_token") || "");
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [backend, setBackend] = useState("checking");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => {
        if (!response.ok) throw new Error("Backend unavailable");
        setBackend("online");
      })
      .catch(() => setBackend("offline"));
  }, []);

  useEffect(() => {
    if (!token) return;
    sessionStorage.setItem("access_token", token);
    fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then((response) => {
      if (!response.ok) {
        sessionStorage.removeItem("access_token");
        setToken("");
      }
    }).catch(() => {});
  }, [token]);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);

    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
      }

      if (!data.access_token) {
        throw new Error("The API response did not contain an access token.");
      }

      sessionStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError(err.message || "Unable to connect to the API.");
    } finally {
      setBusy(false);
    }
  }

  if (token) {
    const originalFetch = window.fetch.bind(window);
    window.fetch = (input, init = {}) => {
      const url = typeof input === "string" ? input : input.url;
      if (!url.startsWith(API_URL)) return originalFetch(input, init);
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      headers.set("Authorization", `Bearer ${sessionStorage.getItem("access_token") || ""}`);
      return originalFetch(input, { ...init, headers });
    };

    return (
      <div className="authenticated-app">
        <div className="auth-toolbar">
          <span>Signed in</span>
          <button onClick={() => {
            sessionStorage.removeItem("access_token");
            setToken("");
          }}>Log out</button>
        </div>
        <App />
      </div>
    );
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <div className="auth-mark">✦</div>
        <h1>Semantic Search AI</h1>
        <p className="auth-subtitle">Your personal knowledge assistant</p>

        <div className="auth-tabs">
          <button type="button" className={mode === "login" ? "selected" : ""} onClick={() => { setMode("login"); setError(""); }}>Login</button>
          <button type="button" className={mode === "register" ? "selected" : ""} onClick={() => { setMode("register"); setError(""); }}>Create account</button>
        </div>

        <label htmlFor="auth-email">Email</label>
        <input id="auth-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required maxLength={254} />

        <label htmlFor="auth-password">Password</label>
        <input id="auth-password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} value={password} onChange={(event) => setPassword(event.target.value)} required minLength={mode === "register" ? 12 : 1} maxLength={128} />

        {mode === "register" && <small>Use at least 12 characters.</small>}
        {error && <div className="auth-error">{error}</div>}

        <button className="auth-submit" type="submit" disabled={busy}>
          {busy ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
        </button>

        <p className="auth-status">
          API status: {backend === "online" ? "Connected" : backend === "offline" ? "Offline" : "Checking"}
        </p>
      </form>
    </main>
  );
}

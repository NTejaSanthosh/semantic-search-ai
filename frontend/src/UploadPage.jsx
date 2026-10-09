
import { useState } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle,
  AlertCircle,
  X,
  LoaderCircle
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const ALLOWED_TYPES = [".pdf", ".docx", ".txt"];
const MAX_FILE_SIZE = 15 * 1024 * 1024;

export default function UploadPage({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [category, setCategory] = useState("General");
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  function selectFiles(event) {
    const selected = Array.from(event.target.files || []);
    const valid = [];
    const messages = [];

    for (const file of selected) {
      const extension = "." + file.name.split(".").pop().toLowerCase();

      if (!ALLOWED_TYPES.includes(extension)) {
        messages.push(`${file.name}: only PDF, DOCX, and TXT files are supported.`);
        continue;
      }

      if (file.size > MAX_FILE_SIZE) {
        messages.push(`${file.name}: file size must not exceed 15 MB.`);
        continue;
      }

      valid.push(file);
    }

    setFiles((current) => {
      const combined = [...current, ...valid];
      return combined.filter(
        (file, index, array) =>
          array.findIndex(
            (item) =>
              item.name === file.name &&
              item.size === file.size &&
              item.lastModified === file.lastModified
          ) === index
      );
    });

    setError(messages.join("\n"));
    event.target.value = "";
  }

  function removeFile(indexToRemove) {
    setFiles((current) =>
      current.filter((_, index) => index !== indexToRemove)
    );
  }

  async function uploadFiles() {
    if (!files.length || uploading) return;

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError("Please log in first. Your access token was not found.");
      return;
    }

    setUploading(true);
    setError("");
    setResults([]);

    const completed = [];

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("category", category.trim() || "General");

        const response = await fetch(`${API_URL}/documents/upload`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData
        });

        const responseText = await response.text();
        let data = {};

        try {
          data = responseText ? JSON.parse(responseText) : {};
        } catch {
          data = { detail: responseText };
        }

        if (!response.ok) {
          throw new Error(
            data.detail || `Upload failed with status ${response.status}.`
          );
        }

        completed.push({
          name: file.name,
          success: true,
          message: data.message || "Uploaded successfully."
        });
      } catch (uploadError) {
        completed.push({
          name: file.name,
          success: false,
          message: uploadError.message || "Upload failed."
        });
      }

      setResults([...completed]);
    }

    setUploading(false);

    const anySucceeded = completed.some((item) => item.success);

    if (anySucceeded) {
      setFiles((current) =>
        current.filter(
          (file) =>
            !completed.some(
              (item) => item.success && item.name === file.name
            )
        )
      );

      if (typeof onUploaded === "function") {
        onUploaded();
      }
    }
  }

  return (
    <section className="upload-page">
      <div className="upload-heading">
        <div className="upload-heading-icon">
          <UploadCloud size={26} />
        </div>
        <div>
          <span className="workspace">KNOWLEDGE SYSTEM</span>
          <h1>Upload Documents</h1>
          <p>
            Add documents to your knowledge base and use them to answer
            questions through Semantic Search AI.
          </p>
        </div>
      </div>

      <div className="upload-card">
        <label className="upload-field">
          <span>Document category</span>
          <input
            type="text"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            placeholder="e.g. HR, Policies, Technical"
            disabled={uploading}
          />
        </label>

        <div className="upload-field">
          <span>Select documents</span>
          <label className="upload-dropzone">
            <UploadCloud size={34} />
            <strong>Choose files to upload</strong>
            <span>PDF, DOCX, or TXT · Maximum 15 MB per file</span>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              multiple
              onChange={selectFiles}
              disabled={uploading}
            />
          </label>
        </div>

        {files.length > 0 && (
          <div className="upload-selected">
            <div className="upload-list-heading">
              <strong>Selected files ({files.length})</strong>
              <span>{uploading ? "Uploading..." : "Ready to upload"}</span>
            </div>

            {files.map((file, index) => (
              <div className="upload-file-row" key={`${file.name}-${file.lastModified}-${index}`}>
                <FileText size={20} />
                <div className="upload-file-info">
                  <strong>{file.name}</strong>
                  <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>
                </div>
                <button
                  type="button"
                  className="upload-remove"
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                  aria-label={`Remove ${file.name}`}
                >
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
        )}

        <button
          type="button"
          className="upload-submit"
          onClick={uploadFiles}
          disabled={uploading || files.length === 0}
        >
          {uploading ? (
            <>
              <LoaderCircle size={18} />
              Uploading documents...
            </>
          ) : (
            <>
              <UploadCloud size={18} />
              Upload {files.length > 0 ? `${files.length} document(s)` : "documents"}
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="upload-message" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="upload-results">
          <h2>Upload results</h2>
          {results.map((result, index) => (
            <div className="upload-result-row" key={`${result.name}-${index}`}>
              {result.success ? (
                <CheckCircle size={20} />
              ) : (
                <AlertCircle size={20} />
              )}
              <div>
                <strong>{result.name}</strong>
                <p>{result.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

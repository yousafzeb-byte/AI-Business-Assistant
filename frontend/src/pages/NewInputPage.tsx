import { useState, useRef, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { recordsService } from "../services/records";
import { Upload, FileText, Loader2 } from "lucide-react";

export default function NewInputPage() {
  const [mode, setMode] = useState<"text" | "file">("text");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "text") {
        if (!content.trim()) {
          setError("Please enter some content");
          setLoading(false);
          return;
        }
        const record = await recordsService.create(
          content,
          title || "Untitled",
        );
        navigate(`/records/${record.id}`);
      } else {
        if (!file) {
          setError("Please select a file");
          setLoading(false);
          return;
        }
        const record = await recordsService.uploadFile(
          file,
          title || file.name,
        );
        navigate(`/records/${record.id}`);
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: string } } })?.response?.data
          ?.error || "Processing failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>New Input</h1>
        <p className="text-muted">
          Paste text or upload a file for AI analysis
        </p>
      </div>

      <div className="card">
        <div className="tab-switcher">
          <button
            className={`tab ${mode === "text" ? "active" : ""}`}
            onClick={() => setMode("text")}
          >
            <FileText size={18} /> Paste Text
          </button>
          <button
            className={`tab ${mode === "file" ? "active" : ""}`}
            onClick={() => setMode("file")}
          >
            <Upload size={18} /> Upload File
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title (optional)</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. January Invoice, Meeting Notes..."
            />
          </div>

          {mode === "text" ? (
            <div className="form-group">
              <label htmlFor="content">Content</label>
              <textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={12}
                placeholder="Paste your invoice, notes, task list, or any business document here..."
              />
            </div>
          ) : (
            <div className="form-group">
              <div
                className="file-drop-zone"
                onClick={() => fileRef.current?.click()}
              >
                <Upload size={32} />
                <p>
                  {file
                    ? file.name
                    : "Click to select a file (PDF, TXT, MD, CSV)"}
                </p>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.txt,.md,.csv"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  hidden
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={18} className="spin" /> Analyzing with AI...
              </>
            ) : (
              "Analyze Content"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

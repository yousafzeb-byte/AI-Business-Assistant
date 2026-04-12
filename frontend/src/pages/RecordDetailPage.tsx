import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { recordsService } from "../services/records";
import type { Record } from "../types";
import {
  ArrowLeft,
  Calendar,
  DollarSign,
  Tag,
  Trash2,
  FileText,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Pencil,
} from "lucide-react";

export default function RecordDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<Record | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusUpdating, setStatusUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editCategory, setEditCategory] = useState("");

  useEffect(() => {
    if (!id) return;
    recordsService
      .get(parseInt(id))
      .then(setRecord)
      .catch(() => navigate("/history"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleDelete = async () => {
    if (!record || !confirm("Delete this record?")) return;
    try {
      await recordsService.delete(record.id);
      navigate("/history");
    } catch {
      setError("Failed to delete record.");
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!record || statusUpdating) return;
    setStatusUpdating(true);
    setError(null);
    try {
      const updated = await recordsService.updateStatus(record.id, newStatus);
      setRecord(updated);
    } catch {
      setError("Failed to update status.");
    } finally {
      setStatusUpdating(false);
    }
  };

  const openEdit = () => {
    if (!record) return;
    setEditTitle(record.title);
    setEditCategory(record.category || "");
    setEditing(true);
  };

  const handleEdit = async () => {
    if (!record) return;
    setError(null);
    try {
      const updated = await recordsService.update(record.id, {
        title: editTitle,
        category: editCategory || undefined,
      });
      setRecord(updated);
      setEditing(false);
    } catch {
      setError("Failed to update record.");
    }
  };

  if (loading || !record) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <Link to="/history" className="btn btn-ghost">
          <ArrowLeft size={18} /> Back
        </Link>
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button className="btn btn-ghost" onClick={openEdit}>
            <Pencil size={18} /> Edit
          </button>
          <div className="status-switcher">
            {["pending", "processed", "archived"].map((s) => (
              <button
                key={s}
                className={`btn btn-sm ${record.status === s ? "btn-status-active" : "btn-ghost"}`}
                onClick={() => handleStatusChange(s)}
                disabled={statusUpdating || record.status === s}
              >
                {statusUpdating ? (
                  <RefreshCw size={14} className="spin" />
                ) : null}
                {s}
              </button>
            ))}
          </div>
          <button className="btn btn-danger" onClick={handleDelete}>
            <Trash2 size={18} /> Delete
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="record-detail">
        <div className="record-header">
          <h1>{record.title}</h1>
          <div className="record-meta">
            {record.category && (
              <span className="badge">
                <Tag size={14} /> {record.category}
              </span>
            )}
            <span className="badge">
              <FileText size={14} /> {record.input_type}
            </span>
            <span className="badge">
              <Calendar size={14} />{" "}
              {new Date(record.created_at).toLocaleDateString()}
            </span>
            {record.total_cost != null && (
              <span className="badge green">
                <DollarSign size={14} /> ${record.total_cost.toFixed(2)}
              </span>
            )}
          </div>
        </div>

        {/* AI Summary */}
        {record.summary && (
          <div className="card">
            <h2>AI Summary</h2>
            <p>{record.summary}</p>
          </div>
        )}

        {/* Extracted Data */}
        {record.extracted_data && (
          <div className="card">
            <h2>Extracted Information</h2>
            <div className="extracted-grid">
              {record.extracted_data.dates?.length > 0 && (
                <div className="extracted-section">
                  <h3>Dates</h3>
                  <ul>
                    {record.extracted_data.dates.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>
              )}

              {record.extracted_data.costs?.length > 0 && (
                <div className="extracted-section">
                  <h3>Costs</h3>
                  <ul>
                    {record.extracted_data.costs.map((c, i) => (
                      <li key={i}>
                        {c.description}: ${c.amount?.toFixed(2)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {record.extracted_data.tasks?.length > 0 && (
                <div className="extracted-section">
                  <h3>Tasks</h3>
                  <ul>
                    {record.extracted_data.tasks.map((t, i) => (
                      <li key={i}>{t}</li>
                    ))}
                  </ul>
                </div>
              )}

              {record.extracted_data.deadlines?.length > 0 && (
                <div className="extracted-section">
                  <h3>Deadlines</h3>
                  <ul>
                    {record.extracted_data.deadlines.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>
              )}

              {record.extracted_data.people?.length > 0 && (
                <div className="extracted-section">
                  <h3>People</h3>
                  <ul>
                    {record.extracted_data.people.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Items */}
        {record.action_items && record.action_items.length > 0 && (
          <div className="card">
            <h2>Suggested Actions</h2>
            <div className="action-list">
              {record.action_items.map((item, i) => (
                <div key={i} className="action-item">
                  <span className={`priority-badge ${item.priority}`}>
                    {item.priority}
                  </span>
                  <span className="action-text">{item.action}</span>
                  {item.priority === "high" ? (
                    <AlertTriangle size={16} className="text-orange" />
                  ) : (
                    <CheckCircle size={16} className="text-green" />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Original Content */}
        <details className="card">
          <summary>
            <h2 style={{ display: "inline" }}>Original Content</h2>
          </summary>
          <pre className="original-content">{record.original_content}</pre>
        </details>
      </div>

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Edit Record</h2>
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                maxLength={255}
              />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select
                value={editCategory}
                onChange={(e) => setEditCategory(e.target.value)}
              >
                <option value="">None</option>
                <option value="invoice">Invoice</option>
                <option value="receipt">Receipt</option>
                <option value="note">Note</option>
                <option value="task">Task</option>
                <option value="contract">Contract</option>
                <option value="report">Report</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="modal-actions">
              <button
                className="btn btn-ghost"
                onClick={() => setEditing(false)}
              >
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleEdit}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

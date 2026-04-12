import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { recordsService } from "../services/records";
import type { Record, PaginatedRecords } from "../types";
import {
  Search,
  FileText,
  Tag,
  Calendar,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export default function HistoryPage() {
  const [data, setData] = useState<PaginatedRecords | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await recordsService.list({
        page,
        search,
        category,
        status,
        per_page: 15,
      });
      setData(result);
    } catch {
      setError("Failed to load records. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page, search, category, status]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const handleSearch = () => {
    setPage(1);
    fetchRecords();
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>History</h1>
      </div>

      <div className="filters-bar">
        <div className="search-input-wrap">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search records..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>

        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Categories</option>
          <option value="invoice">Invoice</option>
          <option value="receipt">Receipt</option>
          <option value="note">Note</option>
          <option value="task">Task</option>
          <option value="contract">Contract</option>
          <option value="report">Report</option>
          <option value="other">Other</option>
        </select>

        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Statuses</option>
          <option value="processed">Processed</option>
          <option value="pending">Pending</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading-screen">
          <div className="spinner" />
        </div>
      ) : !data || data.records.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} />
          <h2>No records found</h2>
          <p>
            Try adjusting your filters or{" "}
            <Link to="/new">create a new input</Link>.
          </p>
        </div>
      ) : (
        <>
          <div className="records-list">
            {data.records.map((record: Record) => (
              <Link
                key={record.id}
                to={`/records/${record.id}`}
                className="record-card"
              >
                <div className="record-card-header">
                  <h3>{record.title}</h3>
                  <span className={`status-badge ${record.status}`}>
                    {record.status}
                  </span>
                </div>
                {record.summary && (
                  <p className="record-summary">
                    {record.summary.slice(0, 150)}...
                  </p>
                )}
                <div className="record-card-meta">
                  {record.category && (
                    <span className="badge">
                      <Tag size={12} /> {record.category}
                    </span>
                  )}
                  <span className="badge">
                    <Calendar size={12} />{" "}
                    {new Date(record.created_at).toLocaleDateString()}
                  </span>
                  {record.total_cost != null && (
                    <span className="badge green">
                      ${record.total_cost.toFixed(2)}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>

          {data.pages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-ghost"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                <ChevronLeft size={18} /> Previous
              </button>
              <span>
                Page {data.page} of {data.pages}
              </span>
              <button
                className="btn btn-ghost"
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next <ChevronRight size={18} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

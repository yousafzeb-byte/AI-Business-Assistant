import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { analyticsService } from "../services/records";
import type { AnalyticsSummary } from "../types";
import {
  FileText,
  DollarSign,
  AlertCircle,
  PlusCircle,
  ArrowRight,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsService
      .getSummary()
      .then(setSummary)
      .catch(() => setError("Failed to load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.full_name?.split(" ")[0]}</h1>
          <p className="text-muted">Here's your business operations overview</p>
        </div>
        <Link to="/new" className="btn btn-primary">
          <PlusCircle size={18} /> New Input
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue">
            <FileText size={24} />
          </div>
          <div className="stat-info">
            <span className="stat-value">{summary?.total_records ?? 0}</span>
            <span className="stat-label">Total Records</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <DollarSign size={24} />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              $
              {(summary?.total_expenses ?? 0).toLocaleString("en-US", {
                minimumFractionDigits: 2,
              })}
            </span>
            <span className="stat-label">Total Expenses</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange">
            <AlertCircle size={24} />
          </div>
          <div className="stat-info">
            <span className="stat-value">
              {summary?.pending_actions?.length ?? 0}
            </span>
            <span className="stat-label">Pending Actions</span>
          </div>
        </div>
      </div>

      {/* Category breakdown */}
      {summary?.categories && Object.keys(summary.categories).length > 0 && (
        <div className="card">
          <h2>Records by Category</h2>
          <div className="category-list">
            {Object.entries(summary.categories).map(([cat, count]) => (
              <div key={cat} className="category-item">
                <span className="category-name">{cat || "uncategorized"}</span>
                <span className="category-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending Actions */}
      {summary?.pending_actions && summary.pending_actions.length > 0 && (
        <div className="card">
          <h2>Pending Action Items</h2>
          <div className="action-list">
            {summary.pending_actions.slice(0, 10).map((action, i) => (
              <div key={i} className="action-item">
                <span className={`priority-badge ${action.priority}`}>
                  {action.priority}
                </span>
                <span className="action-text">{action.action}</span>
                {action.record_id && (
                  <Link
                    to={`/records/${action.record_id}`}
                    className="action-link"
                  >
                    <ArrowRight size={16} />
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

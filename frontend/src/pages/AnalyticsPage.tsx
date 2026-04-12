import { useEffect, useState } from "react";
import { analyticsService } from "../services/records";
import type { AnalyticsSummary } from "../types";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = [
  "#6366f1",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
  "#ec4899",
];

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsService
      .getSummary()
      .then(setSummary)
      .catch(() => setError("Failed to load analytics data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="page">
        {error && <div className="alert alert-error">{error}</div>}
        <p>Failed to load analytics.</p>
      </div>
    );
  }

  const categoryData = Object.entries(summary.categories).map(
    ([name, value]) => ({
      name: name || "uncategorized",
      value,
    }),
  );

  const statusData = Object.entries(summary.statuses).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="page">
      <div className="page-header">
        <h1>Analytics</h1>
        <p className="text-muted">
          Visual insights into your business operations
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-value">{summary.total_records}</span>
            <span className="stat-label">Total Records</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-value">
              $
              {summary.total_expenses.toLocaleString("en-US", {
                minimumFractionDigits: 2,
              })}
            </span>
            <span className="stat-label">Total Expenses</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-info">
            <span className="stat-value">{summary.pending_actions.length}</span>
            <span className="stat-label">Pending Actions</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {categoryData.length > 0 && (
          <div className="card chart-card">
            <h2>Records by Category</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`
                  }
                  outerRadius={100}
                  dataKey="value"
                >
                  {categoryData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {statusData.length > 0 && (
          <div className="card chart-card">
            <h2>Records by Status</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="value"
                  fill="#6366f1"
                  name="Count"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

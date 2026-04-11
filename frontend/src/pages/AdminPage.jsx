import { useState, useEffect } from "react";
import { admin as adminApi } from "../api";

export default function AdminPage() {
  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [recentScans, setRecentScans] = useState([]);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      adminApi.dashboard(),
      adminApi.users(),
      adminApi.scans(),
    ])
      .then(([d, u, s]) => {
        setDashboard(d);
        setUsers(u.users || []);
        setRecentScans(s.scans || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loader"><div className="spinner" /></div>;

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>🛡️ Admin Panel</h1>
        <p>System overview and management</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card glass">
          <span className="stat-icon">👥</span>
          <div className="stat-info">
            <h3>{dashboard?.users || 0}</h3>
            <p>Total Users</p>
          </div>
        </div>
        <div className="stat-card glass">
          <span className="stat-icon">📊</span>
          <div className="stat-info">
            <h3>{dashboard?.scans?.total_scans || 0}</h3>
            <p>Total Scans</p>
          </div>
        </div>
        <div className="stat-card glass">
          <span className="stat-icon">📝</span>
          <div className="stat-info">
            <h3>{dashboard?.feedback_samples || 0}</h3>
            <p>Feedback Samples</p>
          </div>
        </div>
        <div className="stat-card glass">
          <span className="stat-icon">💊</span>
          <div className="stat-info">
            <h3>{dashboard?.supported_medicines || 0}</h3>
            <p>Supported Medicines</p>
          </div>
        </div>
      </div>

      {/* Performance Stats */}
      {dashboard?.scans && (
        <div className="performance-card glass">
          <h2>📈 Model Performance</h2>
          <div className="perf-grid">
            <div className="perf-item">
              <span className="perf-value">{Math.round((dashboard.scans.avg_confidence || 0) * 100)}%</span>
              <span className="perf-label">Avg Confidence</span>
            </div>
            <div className="perf-item">
              <span className="perf-value">{(dashboard.scans.avg_medicines_per_scan || 0).toFixed(1)}</span>
              <span className="perf-label">Avg Medicines/Scan</span>
            </div>
            <div className="perf-item">
              <span className="perf-value">{dashboard.scans.total_warnings || 0}</span>
              <span className="perf-label">Total Warnings</span>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="admin-tabs">
        <button className={`tab-btn ${tab === "overview" ? "active" : ""}`} onClick={() => setTab("overview")}>
          Recent Scans
        </button>
        <button className={`tab-btn ${tab === "users" ? "active" : ""}`} onClick={() => setTab("users")}>
          Users
        </button>
      </div>

      {tab === "users" ? (
        <div className="admin-table glass">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td><span className={`role-badge ${u.role}`}>{u.role}</span></td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="admin-table glass">
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Medicines</th>
                <th>Confidence</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recentScans.map((s) => (
                <tr key={s.id}>
                  <td>{s.filename || "—"}</td>
                  <td>{s.medicines?.length || 0}</td>
                  <td>
                    <span className={`conf-pill ${s.overall_confidence >= 0.7 ? "high" : s.overall_confidence >= 0.4 ? "med" : "low"}`}>
                      {Math.round((s.overall_confidence || 0) * 100)}%
                    </span>
                  </td>
                  <td>{new Date(s.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
